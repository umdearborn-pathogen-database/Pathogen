# FILE NOTE: Line 235 may need additional SQL statements

# Imports
import os
import sys
import pkg_resources

# Variables
# dataDirectory = "Data/Import/data"            # Directory used for ion mobility data import, DO NOT CHANGE    # Uncomment
# metaDataFile = "Data/Import/metadata.csv"     # File used for metadata import, DO NOT CHANGE                  # Uncomment
# \/ USED FOR TESTING, REMOVE AFTER
dataDirectory = "Data/Import/MAI-redo-ecoli"        # <- USED FOR TESTING, REMOVE AFTER
metaDataFile = "Data/Import/info-ecoli-MAI.csv"     # <- USED FOR TESTING, REMOVE AFTER
# /\ USED FOR TESTING, REMOVE AFTER
configFile = "config.yaml"      # Configuration file used for config functions and values, DO NOT CHANGE
# Package list for import management, changes here will reflect what is imported
packages = [
    'pandas',
    'seaborn',
    'scanpy',
    'pyyaml',
    'statsmodels',
    'mysql-connector-python',
    'scipy',
    'pybaselines',
    'mass-suite'
]

# Terminal text coloring
#   Valid inputs <str>: 
#       "30m" (black), "31m" (red), "32m" (green), "33m" (yellow), "34m" (blue), "35m" (magenta),
#       "36m" (cyan), "37m" (white), "1m" (bold), "4m" (underline), "7m" (swap colors foreground/background)
def color(code):
    return f"\033[{code}"

# Prints the welcome message on startup, references the color function for coloring terminal text
def printWelcomeMsg():
    heading = color("4m") + color("32m")
    body = color("0m") + color("36m")
    fileNames = color("33m")
    question = color("33m")
    enter = color("33m")
    reset = color("0m")
    msg = f"""
    {heading}Welcome to Total Analysis USA's Pathogen Database{body}
    Before you begin, please ensure that the following has been completed:
    - Metadata file is a .csv file located at {fileNames}{metaDataFile}{body}
    - Ion mobility data (.csv files) is placed in {fileNames}{dataDirectory}{body} folder
    {question}Is all of the data in the correct place?{body}
    Press {enter}ENTER {body}to continue...
    
    {reset}> """
    x = input(msg)
    if x.strip() != "":
        printWelcomeMsg()
    else:
        print()

# Prints message of types: {"info", "warn", "err"} for logging purposes
def printMessage(msgType, msg):
    if msgType == "info":
        print(color("32m") + "Info: " + str(msg) + (color("0m")))
    elif msgType == "warn":
        print(color("33m") + "Warning: " + str(msg) + (color("0m")))
    elif msgType == "err":
        print(color("31m") + "Error: " + str(msg) + (color("0m")))
    else:
        print(printMessage("err", f"Error printing {msgType}: {msg} with printMessage()") + (color("0m")))

# Installs "package" utilizing subprocess and pip
def install(package):
    import subprocess
    printMessage("info", f"Installing {package}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("\n\n\n")

# Checks whether "package" is already installed to prevent unnecessary downloads
def isInstalled(package):
    installedPackages = {pkg.key for pkg in pkg_resources.working_set}
    if package in installedPackages:
        return True
    return False

# Main package install function to check whether a package found in "packages" list
#   is already installed, if not, installs it. Installed and not installed packages
#   are also displayed to the user.
def installPackages():
    alreadyInstalled = []
    needsInstall = []
    for pkg in packages:
        if isInstalled(pkg):
            alreadyInstalled.append(pkg)
        else:
            needsInstall.append(pkg)
    if alreadyInstalled:
        printMessage("info", f"Packages {alreadyInstalled} already installed")
    if needsInstall:
        printMessage("info", f"Packages {needsInstall} not installed. Installing now...")
        for pkg in needsInstall:
            install(pkg)

# Default config used when config.yaml is not found, utilized for initiating configuration file
defaultConfig = {
    'database': {
        'local-enabled': True,
        'local-file-name': 'pathogens.db',
        'remote-host': '127.0.0.1',
        'remote-port': 3306,
        'remote-database': 'pathogensdb',
        'remote-username': 'admin',
        'remote-password': 'password'
    },
    'options': {
        'cancel-if-null-valued-spectra': False,
        'trim-lower-bounds': 200,
        'trim-upper-bounds': 1995,
        'scaling-factor': 'TIC'
    },
    'align-spectra': {
        'half-window-size': 20,
        'noise-method': 'MAD',
        'SNR': 2,
        'tolerance': 0.002,
        'warping-method': 'lowess',
        'allow-no-matches': False,
        'empty-no-matches': False
    }
}

# Initializes config.yaml on startup
# If config file does not exist, file is created with default values
# If config file does exist, config values are checked to ensure that nothing
#   breaks when referenced
def initializeConfig():
    import yaml
    if not os.path.exists(configFile):
        printMessage("info", f"Config file '{configFile}' does not exist. Creating file with default values...")
        with open(configFile, 'w') as file:
            yaml.dump(defaultConfig, file, default_flow_style=False)
    else:
        checkConfig()
        printMessage("info", f"All configuration values have been checked.")
    localEnabled = getConfigValue('database', 'local-enabled', bool)

# Gets config values located at root.branch, casts them to castType, then returns
#   the casted value for use in the program
def getConfigValue(root, branch, castType):
    import yaml
    filePath = os.path.join(os.getcwd(), configFile)
    try:
        with open(filePath, 'r') as file:
            config = yaml.safe_load(file)
        if root in config and branch in config[root]:
            value = config[root][branch]
            return castType(value)
        else:
            printMessage("err", f"Cannot retrieve config value. '{root}' or '{branch}' not found in configuration file.")
            return None
    except (yaml.YAMLError, OSError) as e:
        printMessage("err", f"Failed to load configuration file: {e}")
        return None
    except (ValueError, TypeError) as e:
        printMessage("err", f"Failed to cast value to {castType.__name__}: {e}")
        return None

# Checks config values to ensure that all values are of the correct type
def checkConfig():
    x = getConfigValue('database', 'local-enabled', bool)
    if x:
        getConfigValue('database', 'remote-host', str)
        getConfigValue('database', 'remote-port', int)
        getConfigValue('database', 'remote-database', str)
        getConfigValue('database', 'remote-username', str)
        getConfigValue('database', 'remote-password', str)
    else:
        getConfigValue('database', 'local-file-name', str)
        getConfigValue('options', 'cancel-if-null-valued-spectra', bool)
        getConfigValue('options', 'trim-lower-bounds', int)
        getConfigValue('options', 'trim-upper-bounds', int)
        getConfigValue('options', 'scaling-factor', str)
        getConfigValue('align-spectra', 'half-window-size', int)
        getConfigValue('align-spectra', 'noise-method', str)
        getConfigValue('align-spectra', 'SNR', int)
        getConfigValue('align-spectra', 'tolerance', float)
        getConfigValue('align-spectra', 'warping-method', str)
        getConfigValue('align-spectra', 'allow-no-matches', bool)
        getConfigValue('align-spectra', 'empty-no-matches', bool)

# Set to None originally in case config values have errors if not using certain database,
#   For instance, if local is being used, there is no need to check remote database values
localEnabled = None
localFileName = None
host = None
port = None
database = None
username = None
password = None

# Main database function
#   Checks which type of database is being used, initializes the database on
#       startup when initialize=True and sends a message to the user.
#       When initialize=False, function acts as a method of communication 
#       with the database, sending the "statement" and either returning one or 
#       all lines that the database sends utilizing "fetchOne"
#   If not localEnabled, config values for remote database connection are assigned
def database(statement, initialize=False, fetchOne=True):
    localEnabled = getConfigValue('database', 'local-enabled', bool)
    connection = None
    def executeQuery(cursor):
        cursor.execute(statement)
        return cursor.fetchone() if fetchOne else cursor.fetchall()
    def logInfo(cursor):
        if not localEnabled:
            cursor.execute("SELECT DATABASE();")
            printMessage("info", f"Connected to MySQL Server version {info}, database: {cursor.fetchone()}")
        else:
            cursor.execute("SELECT sqlite_version();")
            printMessage("info", f"Connected to SQLite Server version {cursor.fetchone()[0]}, connected locally at {localFileName}")
    try:
        if not localEnabled:
            host = getConfigValue('database', 'remote-host', str)
            port = getConfigValue('database', 'remote-port', int)
            database = getConfigValue('database', 'remote-database', str)
            username = getConfigValue('database', 'remote-username', str)
            password = getConfigValue('database', 'remote-password', str)
            info = connection.get_server_info()
            printMessage("warn", "MySQL database is being used. If you believe this to be an error, please check the config values.")
            import mysql.connector
            connection = mysql.connector.connect(host=host, port=port, database=database, user=username, password=password)
        else:
            localFileName = getConfigValue('database', 'local-file-name', str)
            printMessage("warn", "Local database is being used. If you believe this to be an error, please check the config values.")
            import sqlite3
            connection = sqlite3.connect(localFileName)
        cursor = connection.cursor()
        if initialize:
            logInfo(cursor)
#CREATE INITIALIZATION TABLES HERE
            cursor.execute("CREATE TABLE IF NOT EXISTS metadata (ID INT PRIMARY KEY, orig VARCHAR(255), experiment VARCHAR(255), location VARCHAR(255), bacteria VARCHAR(255));")
            cursor.execute("CREATE TABLE IF NOT EXISTS massspec (ID INT, mass DOUBLE, intensity DOUBLE, PRIMARY KEY (ID, mass), FOREIGN KEY (ID) REFERENCES metadata(ID));")
        else:
            return executeQuery(cursor)
    except (mysql.connector.Error if not localEnabled else sqlite3.Error) as e:
        printMessage("err", f"Issue connecting to the {'MySQL' if not localEnabled else 'local'} database: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def getColumnValues(dataframesList, colName):
    for index, data in enumerate(dataframesList):
        if data.shape[1] < 2:
            printMessage("err", f"DataFrame at index {index} must contain at least two columns.")
        else:
            return data[colName].values