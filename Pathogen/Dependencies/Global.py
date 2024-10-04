import os
import sys
import pkg_resources

# Variables
# massSpecDataDirectory = "Data/Import/mass-spec-data"
# TEMP REMOVE
massSpecDataDirectory = "Data/Import/MAI-redo-ecoli"
# metaDataFile = "Data/Import/metadata.csv"
# TEMP REMOVE
metaDataFile = "Data/Import/info-ecoli-MAI.csv"
configFile = "config.yaml"
packages = [
    'pandas',
    'seaborn',
    'scanpy',
    'pyyaml',
    'statsmodels',
    'mysql-connector-python',
    'scipy',
    'pybaselines'
]

# Escape codes
#   
#   \033[ - Escape character
#   0m - Resets the formatting to default
#   
#   Coloring:
#       30m - Black
#       31m - Red
#       32m - Green
#       33m - Yellow
#       34m - Blue
#       35m - Magenta
#       36m - Cyan
#       37m - White
#   Styles:
#       1m - Bold
#       4m - Underline
#       7m - Swap colors foreground and background
def color(code):
    return f"\033[{code}"

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
    - Mass spectrometry data (.csv files) is placed in {fileNames}{massSpecDataDirectory}{body} folder
    {question}Is all of the data in the correct place?{body}
    Press {enter}ENTER {body}to continue...
    
    {reset}> """
    x = input(msg)
    if x.strip() != "":
        printWelcomeMsg()
    else:
        print()

def printMessage(msgType, msg):
    if msgType == "info":
        print(color("32m") + "Info: " + str(msg) + (color("0m")))
    elif msgType == "warn":
        print(color("33m") + "Warning: " + str(msg) + (color("0m")))
    elif msgType == "err":
        print(color("31m") + "Error: " + str(msg) + (color("0m")))
    else:
        print(printMessage("err", f"Error printing {msgType}: {msg} with printMessage()") + (color("0m")))

def install(package):
    import subprocess
    printMessage("info", f"Installing {package}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("\n\n\n")
    
def isInstalled(package):
    installedPackages = {pkg.key for pkg in pkg_resources.working_set}
    if package in installedPackages:
        return True
    return False

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

import yaml

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
        'remove-null-valued-spectra': False,
        'cancel-if-sum-is-zero': False,
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

def initializeConfig():
    if not os.path.exists(configFile):
        printMessage("info", f"Config file '{configFile}' does not exist. Creating file with default values...")
        with open(configFile, 'w') as file:
            yaml.dump(defaultConfig, file, default_flow_style=False)
    else:
        checkConfig()
        printMessage("info", f"All configuration values have been checked.") 

def getConfigValue(root, branch, castType):
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
        getConfigValue('options', 'remove-null-valued-spectra', bool)
        getConfigValue('options', 'cancel-if-sum-is-zero', bool)
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

# def initializeConfig(configFile="config.yaml", defaultConfig=defaultConfig):
#     if not os.path.exists(configFile):
#         print(f"Config file '{configFile}' does not exist. Creating with default values...")
#         saveConfig(configFile, defaultConfig)
#     else:
#         checkConfigValues()

# def saveConfig(configFile, configData):
#     with open(configFile, 'w') as file:
#         yaml.dump(configData, file, default_flow_style=False)

# def getConfig(filePath):
#     with open(filePath, 'r') as file:
#         return yaml.safe_load(file)

# def getConfigValue(root, branch):
#     fileName = 'config.yaml'
#     filePath = os.path.join(os.getcwd(), fileName)
#     config = getConfig(filePath)
#     if root in config and branch in config[root]:
#         return config[root][branch]
#     else:
#         log(f"Error retrieving value. {root} or {branch} not found in the configuration file.")

# def checkConfigValues():
#     x = getConfigValueCasted('database', 'local-enabled', bool)
#     getConfigValueCasted('database', 'local-file-name', str)
#     if x:
#         getConfigValueCasted('database', 'remote-host', str)
#         getConfigValueCasted('database', 'remote-port', int)
#         getConfigValueCasted('database', 'remote-database', str)
#         getConfigValueCasted('database', 'remote-username', str)
#         getConfigValueCasted('database', 'remote-password', str)
#     getConfigValueCasted('options', 'remove-null-valued-spectra', bool)
#     getConfigValueCasted('options', 'cancel-if-sum-is-zero', bool)
#     getConfigValueCasted('options', 'trim-lower-bounds', int)
#     getConfigValueCasted('options', 'trim-upper-bounds', int)
#     getConfigValueCasted('options', 'scaling-factor', str)
#     getConfigValueCasted('align-spectra', 'half-window-size', int)
#     getConfigValueCasted('align-spectra', 'noise-method', str)
#     getConfigValueCasted('align-spectra', 'SNR', int)
#     getConfigValueCasted('align-spectra', 'tolerance', float)
#     getConfigValueCasted('align-spectra', 'warping-method', str)
#     getConfigValueCasted('align-spectra', 'allow-no-matches', bool)
#     getConfigValueCasted('align-spectra', 'empty-no-matches', bool)

# def getConfigValueCasted(root, branch, castType):
#     x = getConfigValue(root, branch)
#     try:
#         return castType(x)
#     except (ValueError, TypeError):
#         return None

# localEnabled decides which set of values to check against
localEnabled = getConfigValue('database', 'local-enabled', bool)
# Set to None originally in case config values have casting errors
localFileName = None
host = None
port = None
database = None
username = None
password = None

def database(statement, initialize=False, fetchOne=True):
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