FROM python:3.8.10-slim-buster
LABEL description="CIDOC-QA Service Component"
WORKDIR /deploy

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "5000"]

EXPOSE 5000
