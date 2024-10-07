import logging

from rapidfuzz import fuzz
from src.database import PostgresRepository

class NamesRepository:
    def calculate_similarity(self, input_name: str, threshold: int) -> dict:
        # validate input
        if not input_name:
            logging.error("No input name provided.")
            raise ValueError("Input name must be provided.")        
        if not (0 <= threshold <= 100):
            logging.error(f"Invalid threshold: {threshold}. Must be between 0 and 100.")
            raise ValueError("Threshold must be between 0 and 100.")
        # initialize psql repo, record logs
        postgres_repository = PostgresRepository()
        postgres_repository.insert_logs(input_name, threshold)
        names = postgres_repository.get_names()
        # add names above similarity threshold
        results = {}
        input_name_lower = input_name.lower()
        for name in names:
            full_name_lower = name['full_name_cleaned'].lower()
            similarity = fuzz.ratio(input_name_lower, full_name_lower)
            if similarity >= threshold:
                logging.info(f"{input_name_lower} vs {full_name_lower} - match found, similarity is {similarity}")
                results[name['id']] = {
                    "full_name": name['full_name'],
                    "similarity": similarity
                }
        # sort results
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1]['similarity'], reverse=True)
        )
        logging.info(f"Returning {len(sorted_results)} results with a similarity above {threshold}.")
        return sorted_results
