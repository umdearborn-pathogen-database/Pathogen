from ConfigurationFile.Config import getConfigValueCasted
from ConfigurationFile.Config import log
from Dependencies.Setup import install

localEnabled = getConfigValueCasted('database', 'local-enabled', bool)
localFileName = getConfigValueCasted('database', 'local-file-name', str)
host = getConfigValueCasted('database', 'remote-host', str)
port = getConfigValueCasted('database', 'remote-port', int)
database = getConfigValueCasted('database', 'remote-database', str)
username = getConfigValueCasted('database', 'remote-username', str)
password = getConfigValueCasted('database', 'remote-password', str)

# Check type of database and initialize
def initializeDatabase():
    if(not localEnabled):
        log("MySQL database is being used. If you believe this is an error, check the config values.")
        install('mysql.connector')
        import mysql.connector
        from mysql.connector import Error
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            if connection.is_connected():
                dbInfo = connection.get_server_info()
                log(f"Connected to MySQL Server version {dbInfo}")
                cursor = connection.cursor()
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                log(f"Connected to database: {record}")
        except Error as e:
            log(f"Error while connecting to MySQL: {e}")
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
    else:
        log("Local database is being used. If you believe this is an error, check the config values.")
        import sqlite3
        conn = None
        try:
            conn = sqlite3.connect(localFileName)
            log(f"Database connected at {localFileName}")
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            log(f"SQLite version: {version[0]}")
        except sqlite3.Error as e:
            log(f"Error connecting to the database: {e}")
        finally:
            if conn is not None:
                conn.close()

# SQLite Handler


# MySQL Handler

