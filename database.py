import sqlite3
import pandas as pd


class DatabaseInterface():
    def __init__(self, database_name):
        self.database_name = database_name

    def insert_summary_data(self, hash, gps_distance, submitted_distance):
        con = sqlite3.connect(self.database_name)
        cur = con.cursor()
        query = f"""insert or replace into calib (file_hash,gps_distance_miles,user_distance_miles) VALUES ("{hash}",{gps_distance},{submitted_distance});"""
        print(query)
        cur.execute(query)
        con.commit()
