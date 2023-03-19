#!/usr/bin/python

import psycopg2
import json


class DataIbge():
    def __init__(self) -> None:

        self.conn = psycopg2.connect(database="ibge", user = "postgres", password="12345", host = "127.0.0.1", port = "5432")
        print("Opened database successfully")

        self.cur = self.conn.cursor()
        
        self.names = {}

        

    def checkName(self, name):
        if name in self.names:
            self.names[name] = self.names[name] + 1
            return True
        else:
            return False

    def getName(self,name):
        return self.cur.execute(f"SELECT data FROM ibge WHERE name = {name}")

    def addName(self,name, data):
        self.names[name] = 1
        self.cur.execute(f"INSERT INTO ibge (name, data) VALUES(%s,%s);", (name, data))
        self.conn.commit()
