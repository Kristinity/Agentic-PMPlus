FROM python:3.12-slim

WORKDIR /app

# Bewusst KEINE requirements.txt: server.py nutzt ausschliesslich die Python-
# Standardbibliothek (http.server/urllib) - siehe README.md fuer die Stack-Begruendung.
COPY server.py .
COPY public/ public/

EXPOSE 8080

CMD ["python", "server.py"]
