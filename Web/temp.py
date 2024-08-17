import json
import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='',
            database='rs',
            user='',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return None

def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        
        cursor.execute("DESCRIBE tbl_client_coverage")
        columns = [column[0].lower() for column in cursor.fetchall()]
        
        for item in data:
            insert_data = {}
            for key, value in item.items():
                if key.lower() in columns:
                    insert_data[key.lower()] = value
            
            fields = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            sql = f"INSERT INTO tbl_client_coverage ({fields}) VALUES ({placeholders})"
            
            # Execute the query
            cursor.execute(sql, list(insert_data.values()))
        
        connection.commit()
        print(f"Successfully inserted {len(data)} records.")
    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()

def main():
    # Load JSON data
    with open('your_json_file.json', 'r') as file:
        json_data = json.load(file)
    
    # Connect to the database
    connection = connect_to_database()
    if connection is None:
        return
    
    # Insert data
    insert_data(connection, json_data)
    
    # Close the connection
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

if __name__ == "__main__":
    main()