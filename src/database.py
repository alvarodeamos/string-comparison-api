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

    def create_names_table(self):
        logging.info("start creating names table")
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # create table if it does not exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS names_data (
                    id SERIAL PRIMARY KEY,
                    logical_id INTEGER,
                    full_name VARCHAR,
                    full_name_cleaned VARCHAR
                );
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"error while creating logs table: {e}")
        finally:
            cur.close()
            conn.close()

    def create_logs_table(self):
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

    def insert_names(self):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # clean data from names
            cur.execute("DELETE FROM names_data;")
            conn.commit()
            # load data from CSV
            with open('names_dataset.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    logical_id = row['ID']
                    full_name = row['Full Name']
                    cur.execute("""
                    INSERT INTO names_data (logical_id, full_name, full_name_cleaned)
                    VALUES (%s, %s,
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    %s, 
                                    '^\w+\.\s*', '', 'g'
                                ),
                                '[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', 'g'
                            ),
                            '\s{2,}', ' ', 'g'
                        )
                    );
                    """, (logical_id, full_name, full_name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"error while inserting names: {e}")
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

    def get_names(self):
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT id, full_name, full_name_cleaned FROM names_data;")
            results = cur.fetchall()
            return results
        except Exception as e:
            logging.error(f"error while retrieving names: {e}")
        finally:
            cur.close()
            conn.close()
