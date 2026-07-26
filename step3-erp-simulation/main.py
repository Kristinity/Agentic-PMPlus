"""
step3-erp-simulation - Agentic-PMPlus

Liest ein Unternehmensprofil (YAML, siehe company_profile.example.yaml) und
generiert daraus ein zusammenhaengendes Set simulierter ERP-CSV-Tabellen in
shared/data/, das in Step 4/5 weiterverwendet wird.
"""

import os
import random
from datetime import date, timedelta

import pandas as pd
import yaml
from faker import Faker

PROFILE_PATH = os.environ.get(
    "COMPANY_PROFILE",
    os.path.join(os.path.dirname(__file__), "company_profile.example.yaml"),
)
# Relativ zu WORKDIR /app im Container -> entspricht dem gemounteten
# ./shared/data:/app/shared_data aus docker-compose.yml.
OUTPUT_DIR = os.environ.get("SHARED_DATA_DIR", "shared_data")

DAY_NAME_BY_WEEKDAY = {0: "Mo", 1: "Di", 2: "Mi", 3: "Do", 4: "Fr", 5: "Sa", 6: "So"}


def load_profile(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_range(value):
    """[min, max] -> (min, max); Skalar -> (value, value)."""
    if isinstance(value, (list, tuple)):
        return value[0], value[1]
    return value, value


def parse_due_date_distribution(spec):
    """'uniform(3,14)' -> Funktion(rng) -> Tage bis Liefertermin."""
    inner = spec[spec.index("(") + 1: spec.index(")")]
    low, high = (int(x.strip()) for x in inner.split(","))
    return lambda rng: rng.randint(low, high)


def write_csv(rows, fieldnames, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    pd.DataFrame(rows, columns=fieldnames).to_csv(path, index=False)
    return path


def generate_bom(products):
    return [
        {
            "product_id": product["id"],
            "component": component["component"],
            "quantity": component["quantity"],
            "lead_time_days": component["lead_time_days"],
        }
        for product in products
        for component in product.get("bom", [])
    ]


def generate_routings(products):
    return [
        {
            "product_id": product["id"],
            "sequence": seq,
            "operation": op["operation"],
            "work_center": op["work_center"],
            "duration_minutes": op["duration_minutes"],
            "setup_minutes": op["setup_minutes"],
        }
        for product in products
        for seq, op in enumerate(product.get("routing", []), start=1)
    ]


def generate_work_centers(resources):
    return [
        {
            "work_center_id": wc["id"],
            "capacity_hours_per_shift": wc["capacity_hours_per_shift"],
            "shifts_per_day": wc["shifts_per_day"],
            "availability_pct": wc["availability_pct"],
        }
        for wc in resources.get("work_centers", [])
    ]


def generate_calendar(resources, start_date, weeks):
    calendar_cfg = resources.get("calendar", {})
    working_days = set(calendar_cfg.get("working_days", []))
    holidays = set(calendar_cfg.get("holidays", []))

    rows = []
    for i in range(weeks * 7):
        current = start_date + timedelta(days=i)
        iso = current.isoformat()
        is_holiday = iso in holidays
        is_working = DAY_NAME_BY_WEEKDAY[current.weekday()] in working_days and not is_holiday
        rows.append({"date": iso, "is_working_day": is_working, "is_holiday": is_holiday})
    return rows


def generate_orders(profile, products, start_date, weeks, rng, faker):
    demand = profile["demand"]
    orders_per_week = demand["orders_per_week"]
    rush_share = demand.get("rush_order_share", 0.0)
    due_date_sampler = parse_due_date_distribution(demand["due_date_distribution"])
    seasonality = demand.get("seasonality")

    rows = []
    order_counter = 1
    for week in range(weeks):
        week_orders = orders_per_week
        # Einfache Saisonalitaet: letztes Viertel des Simulationshorizonts
        # staerker gewichten, falls im Profil "Q4-peak" angegeben ist.
        if seasonality == "Q4-peak" and week >= weeks - max(1, weeks // 4):
            week_orders = int(orders_per_week * 1.5)

        for _ in range(week_orders):
            product = rng.choice(products)
            variant_idx = rng.randint(1, product.get("variants", 1))
            order_date = start_date + timedelta(days=week * 7 + rng.randint(0, 6))
            due_in_days = due_date_sampler(rng)
            is_rush = rng.random() < rush_share
            order_id = f"O-{order_counter:05d}"
            order_counter += 1
            rows.append({
                "order_id": order_id,
                "customer": faker.company(),
                "product_id": product["id"],
                "variant": f"{product['id']}-V{variant_idx}",
                "order_date": order_date.isoformat(),
                "due_date": (order_date + timedelta(days=due_in_days)).isoformat(),
                "is_rush": is_rush,
                "priority": "hoch" if is_rush else "normal",
                "quantity": rng.randint(1, 20),  # keine Verteilung im Profil vorgegeben
            })
    return rows


def generate_disruptions(profile, orders, weeks, rng):
    rows = []
    for disruption in profile.get("disruptions", []):
        d_type = disruption["type"]

        if d_type == "machine_breakdown":
            low, high = parse_range(disruption["downtime_hours"])
            for week in range(weeks):
                if rng.random() < disruption["probability_per_week"]:
                    rows.append({
                        "week": week,
                        "type": d_type,
                        "target": disruption["work_center"],
                        "impact": round(rng.uniform(low, high), 1),
                        "unit": "hours",
                    })

        elif d_type == "material_shortage":
            low, high = parse_range(disruption["delay_days"])
            for week in range(weeks):
                if rng.random() < disruption["probability_per_week"]:
                    rows.append({
                        "week": week,
                        "type": d_type,
                        "target": disruption["component"],
                        "impact": rng.randint(low, high),
                        "unit": "days",
                    })

        elif d_type == "priority_change":
            prob = disruption["probability_per_order"]
            for order in orders:
                if rng.random() < prob:
                    rows.append({
                        "week": "",  # keine Wochenbindung, betrifft einen einzelnen Auftrag
                        "type": d_type,
                        "target": order["order_id"],
                        "impact": "hoch" if order["priority"] != "hoch" else "normal",
                        "unit": "priority",
                    })
    return rows


def generate_inventory(bom_rows, safety_factor=1.5):
    rows = []
    seen = set()
    for bom in bom_rows:
        component = bom["component"]
        if component in seen:
            continue
        seen.add(component)
        safety_stock = int(bom["quantity"] * bom["lead_time_days"] * safety_factor)
        rows.append({
            "component": component,
            "safety_stock": safety_stock,
            "current_stock": safety_stock,
        })
    return rows


def main():
    profile = load_profile(PROFILE_PATH)
    sim_cfg = profile.get("simulation", {})
    weeks = sim_cfg.get("weeks", 12)
    seed = sim_cfg.get("random_seed", 42)
    rng = random.Random(seed)
    faker = Faker()
    faker.seed_instance(seed)
    start_date = date.today()

    products = profile["products"]
    resources = profile["resources"]

    bom_rows = generate_bom(products)
    routing_rows = generate_routings(products)
    work_center_rows = generate_work_centers(resources)
    calendar_rows = generate_calendar(resources, start_date, weeks)
    order_rows = generate_orders(profile, products, start_date, weeks, rng, faker)
    disruption_rows = generate_disruptions(profile, order_rows, weeks, rng)
    inventory_rows = generate_inventory(bom_rows)

    write_csv(bom_rows, ["product_id", "component", "quantity", "lead_time_days"], "bom.csv")
    write_csv(
        routing_rows,
        ["product_id", "sequence", "operation", "work_center", "duration_minutes", "setup_minutes"],
        "routings.csv",
    )
    write_csv(
        work_center_rows,
        ["work_center_id", "capacity_hours_per_shift", "shifts_per_day", "availability_pct"],
        "work_centers.csv",
    )
    write_csv(calendar_rows, ["date", "is_working_day", "is_holiday"], "calendar.csv")
    write_csv(
        order_rows,
        ["order_id", "customer", "product_id", "variant", "order_date", "due_date", "is_rush", "priority", "quantity"],
        "orders.csv",
    )
    write_csv(disruption_rows, ["week", "type", "target", "impact", "unit"], "disruptions.csv")
    write_csv(inventory_rows, ["component", "safety_stock", "current_stock"], "inventory.csv")

    print("=== step3-erp-simulation ===")
    print(f"Profil: {PROFILE_PATH}")
    print(
        f"Erzeugt: {len(order_rows)} Auftraege, {len(disruption_rows)} Stoerungen "
        f"ueber {weeks} Wochen -> {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
