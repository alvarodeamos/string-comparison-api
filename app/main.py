import logging

from fastapi import FastAPI, Query
from src.database import PostgresRepository
from src.names import NamesRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()


@app.on_event("startup")
def startup_event():
    logging.info("startup event triggered")
    postgres_repository = PostgresRepository()
    logging.info("inserting names...")
    postgres_repository.insert_names()
    logging.info("names inserted")
    logging.info("creating logs table...")
    postgres_repository.create_logs()
    logging.info("logs table created")


@app.get("/similarity")
def calculate_name_similarity(
    input_name: str = Query(..., min_length=1, description="full name to compare"),
    threshold: int = Query(80, ge=0, le=100, description="similarity threshold (0-100)")
):
    logging.info(f"retrieving similar names to {input_name}, threshold {threshold}")
    names_repository = NamesRepository()
    results = names_repository.calculate_similarity(input_name, threshold)
    return results
