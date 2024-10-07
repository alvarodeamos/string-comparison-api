import csv
import logging
import os
import psycopg2

from psycopg2.extras import RealDictCursor


class PostgresRepository:
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")

    def get_connection(self):
        conn = psycopg2.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD
        )
        return conn

    def insert_names(self):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # create table if it does not exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS names_data (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR NOT NULL
                );
            """)
            # clear existing data
            cur.execute("DELETE FROM names_data;")
            # load data from CSV
            with open('names_dataset.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    full_name = row['full_name']
                    cur.execute("INSERT INTO names_data (full_name) VALUES (%s);", (full_name,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"error while inserting names: {e}")
        finally:
            cur.close()
            conn.close()

    def create_logs(self):
        logging.info("start creating logs table")
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # create table if it does not exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_logs (
                    id SERIAL PRIMARY KEY,
                    full_name_searched VARCHAR,
                    threshold_searched INT,
                    insert_time timestamptz null default now()
                );
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"error while creating logs table: {e}")
        finally:
            cur.close()
            conn.close()

    def get_names(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT id, full_name FROM names_data;")
            results = cur.fetchall()
            return results
        except Exception as e:
            logging.error(f"error while retrieving names: {e}")
        finally:
            cur.close()
            conn.close()

    def insert_logs(self, full_name:str, threshold: int):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO search_logs (full_name_searched, threshold_searched) VALUES (%s, %s);", (full_name,threshold,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"error while inserting logs: {e}")
        finally:
            cur.close()
            conn.close()

