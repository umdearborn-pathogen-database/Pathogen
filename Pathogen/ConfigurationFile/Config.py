from Dependencies.Setup import install

install('pyyaml')
import yaml
import os

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
    'logging': {
        'logging-enabled': False,
        'logging-output-file': 'pathogens.log'
    },
    'options': {
        'remove-null-valued-spectra': False,
        'cancel-if-sum-is-zero': False,
        'trim-lower-bounds': 200,
        'trim-upper-bounds': 1995,
        'scaling-factor': 'TIC'
    }
}

def initializeConfig(configFile="config.yaml", defaultConfig=defaultConfig):
    if not os.path.exists(configFile):
        print(f"Config file '{configFile}' does not exist. Creating with default values...")
        saveConfig(configFile, defaultConfig)
    else:
        checkConfigValues()
        log("All configuration values have been checked. See log for any issues.")

def saveConfig(configFile, configData):
    with open(configFile, 'w') as file:
        yaml.dump(configData, file, default_flow_style=False)

def getConfig(filePath):
    with open(filePath, 'r') as file:
        return yaml.safe_load(file)

def getConfigValue(root, branch):
    fileName = 'config.yaml'
    filePath = os.path.join(os.getcwd(), fileName)
    config = getConfig(filePath)
    if root in config and branch in config[root]:
        return config[root][branch]
    else:
        log(f"Error retrieving value. {root} or {branch} not found in the configuration file.")

def checkConfigValues():
    x = getConfigValueCasted('database', 'local-enabled', bool)
    getConfigValueCasted('database', 'local-file-name', str)
    if x:
        getConfigValueCasted('database', 'remote-host', str)
        getConfigValueCasted('database', 'remote-port', int)
        getConfigValueCasted('database', 'remote-database', str)
        getConfigValueCasted('database', 'remote-username', str)
        getConfigValueCasted('database', 'remote-password', str)
    getConfigValueCasted('logging', 'logging-enabled', bool)
    getConfigValueCasted('logging', 'logging-output-file', str)
    getConfigValueCasted('options', 'remove-null-valued-spectra', bool)
    getConfigValueCasted('options', 'cancel-if-sum-is-zero', bool)
    getConfigValueCasted('options', 'trim-lower-bounds', int)
    getConfigValueCasted('options', 'trim-upper-bounds', int)
    getConfigValueCasted('options', 'scaling-factor', str)

def getConfigValueCasted(root, branch, castType):
    x = getConfigValue(root, branch)
    try:
        return castType(x)
    except (ValueError, TypeError):
#        log(f"Failed to cast value '{x}' to {castType.__name__}")
        return None

# Specific Methods
def log(msg):
    print(msg)
    if getConfigValueCasted('logging', 'logging-enabled', bool):
        fileName = getConfigValueCasted('logging', 'logging-output-file')
        with open(fileName, "a") as file:
            file.write(f"{msg}\n")