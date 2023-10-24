#!/usr/bin/python3
# bit of test script - not needed
import mysql.connector

mydb = mysql.connector.connect(
  host="erminserver.localdomain",
  database="metminidb",
  user="metmini",
  password="metmini"
)

mycursor = mydb.cursor()

sql = "INSERT INTO metminilogs (pressure, ptrend, wind_dir) VALUES (%s, %s, %s)"
val = (1023, "Rising", "NNE")
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
