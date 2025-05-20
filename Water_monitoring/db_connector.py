import mysql.connector

def insert_data(water_level, water_distance, temperature, warnings):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="water_monitor"
        )
        
        cursor = conn.cursor()
        
        if isinstance(warnings, list):
            warnings = ', '.join(warnings)


        cursor.execute("INSERT INTO tbl_water_and_temp (water_level, water_distance, temperature, warnings) VALUES (%s, %s, %s, %s)", (water_level, water_distance, temperature, warnings))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database insert error:", e)
