import streamlit as st
import math
import mysql.connector
import pandas as pd  # Import Pandas
import requests
from geopy.geocoders import Nominatim
import numpy as np
from urllib.parse import quote

# Replace these values with your actual MySQL connection details
host = "localhost"      # Endpoint or hostname
user = "root"
password = "mySQL_DevX@123"
database = "legalease_db"
port = "3306"       # Port number
        
def get_current_location():
    try:
        # Send a request to the ipinfo.io API to get the current location
        response = requests.get('https://ipinfo.io')
        data = response.json()

        # Extract latitude and longitude
        loc = data.get('loc', 'Unknown').split(',')
        latitude, longitude = loc[0], loc[1]

        return latitude, longitude

    except Exception as e:
        st.error(f"Error getting current location: {e}")
        return None, None
    
# Function to get nearby police stations using Google Places API
def get_police_stations_nearby(api_key, latitude, longitude, radius=5000, limit=5):
    try:
        # Google Places API endpoint for searching nearby places
        endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        # Set parameters for the API request
        params = {
            'location': f'{latitude},{longitude}',
            'radius': radius,
            'type': 'police',
            'key': api_key
        }

        # Send request to the Google Places API
        response = requests.get(endpoint, params=params)
        data = response.json()

        # Extract and return police station names and coordinates
        results = data.get('results', [])
        police_stations = [{'name': result['name'], 'coordinates': result['geometry']['location']} for result in results[:limit]]
        return police_stations

    except Exception as e:
        st.error(f"Error getting nearby police stations: {e}")
        return []


        
# Function to establish a MySQL connection
def create_connection():
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    return connection

# Function to execute a query and fetch data
def execute_and_fetch(connection, query, data=None):
    cursor = connection.cursor()

    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
        connection.commit()
        return result
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        connection.rollback()
        return None
    finally:
        cursor.close()

# Function to create the 'recentcases' table
def create_recentcases_table(connection):
    query = """
    CREATE TABLE IF NOT EXISTS recentcases (
        sno INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200),
        url VARCHAR(255),
        description VARCHAR(500)
    );
    """
    execute_and_fetch(connection, query)

# Function to insert sample data into 'recentcases' table
def insert_sample_data(connection):
    query = """
    INSERT INTO recentcases (title, url, description)
    VALUES (%s, %s, %s);
    """
    data = [
        ("Case 1", "https://example.com/case1", "Description for Case 1"),
        ("Case 2", "https://example.com/case2", "Description for Case 2"),
        # Add more sample data as needed
    ]
    for entry in data:
        execute_and_fetch(connection, query, entry)

# Function to fetch all rows from a table
def fetch_all_rows(connection, table_name):
    query = f"SELECT * FROM {table_name};"
    return execute_and_fetch(connection, query)

# Function to display the result as a Pandas DataFrame
def display_as_table(data, column_names):
    st.write("Query Result:")
    df = pd.DataFrame(data, columns=column_names)

    # # Modify the 'url' column in the DataFrame to include links
    df['url'] = df.apply(lambda row: f'<a href="{quote(row["url"], safe=":/?=&")}">{row["url"]}</a>', axis=1)
    
    # Display the modified DataFrame with links inside the table
    st.dataframe(df)

def convert_to_link(url_string):
    # Encode the string to make it URL-safe
    encoded_url = quote(url_string, safe=':/?=&')

    # Create the link
    link = f'<a href="{encoded_url}">{url_string}</a>'
    
    return st.markdown(link, unsafe_allow_html=True)

# Streamlit app
def main():
    st.title("MySQL Connection with Streamlit")

    # Connect to MySQL
    connection = create_connection()

    # Check if connection is successful
    if connection.is_connected():
        st.success("Connected to MySQL database!")

        # Create the 'recentcases' table
        create_recentcases_table(connection)
        st.success("Table 'recentcases' created successfully!")

        # Insert sample data into 'recentcases' table
        insert_sample_data(connection)
        st.success("Sample data inserted into 'recentcases' table!")

        table_name = "recentcases"
        data = fetch_all_rows(connection, table_name)

        # Display the result as a table using Pandas
        display_as_table(data, ["sno", "title", "url", "description"])

        # Close the connection
        connection.close()
        st.success("Connection closed.")
        

    # Get current location
    latitude, longitude = get_current_location()

    if latitude is not None and longitude is not None:
        st.write(f"Your current location: Latitude {latitude}, Longitude {longitude}")

        # Display map with a marker for the user's location
        
        data = pd.DataFrame({
            'lat': [float(latitude)],
            'lon': [float(longitude)]
        })

        # Display map with a marker for the user's location
        st.map(data, zoom=12)


       
        
if __name__ == "__main__":
    main()
