import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
cursor = conn.cursor()

#cursor.execute means do, execute command, or tell SQL

cursor.execute("CREATE DATABASE IF NOT EXISTS water_monitor") 

cursor.execute("USE water_monitor")

# If i re reset natin yung data base.
cursor.execute("DROP TABLE IF EXISTS tbl_water_and_temp")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tbl_water_and_temp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    water_level VARCHAR(255),
    water_distance INT,
    temperature FLOAT,
    warnings VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("Database and table created successfully.")
cursor.close()
conn.close()

