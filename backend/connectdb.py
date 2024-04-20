import psycopg2

def get_db_connection():
    # Database connection parameters
    dbname = "database_name"
    user = "username"
    password = "password"
    host = "localhost"
    port = "5432"  # Default PostgreSQL port
    
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        return conn
    except psycopg2.Error as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None