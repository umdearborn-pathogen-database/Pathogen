import os
import sys

def install(package):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("\n\n\n")

def installDependencies():
    install('pandas')
    install('seaborn')
    install('MALDIpy==0.1.1')
    install('scanpy')

install('pyyaml')
import yaml
    
default_config = {
    'database': {
        'local-enabled': 'yes',
        'local-file-name': 'pathogens.db',
        'remote-host': '127.0.0.1',
        'remote-port': '3306',
        'remote-user': 'admin',
        'password': 'password'
    },
    'logging': {
        'logging-enabled': 'false',
        'logging-output': 'pathogens.log'
    },
    'options': {
        'remove-null-valued-spectra': 'false',
        'cancel-if-sum-is-zero': 'false',
        'scaling-factor': 'TIC'
    }
}

def loadConfig():
    file_name = 'pathogen-config.yaml'
    file_path = os.path.join(os.getcwd(), file_name)
    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w') as file:
                yaml.dump(default_config, file, default_flow_style=False)
                print(f"Configuration file successfully created!\nLocation: {file_path}\n")
        except Exception as e:
            print(f"An exception has occurred: {e}")
    else:
        log(f"Configuration file already created and loaded in.\n")

def getConfig(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def saveConfig(file_path, config):
    with open(file_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def getConfigValue(root, branch):
    file_name = 'pathogen-config.yaml'
    file_path = os.path.join(os.getcwd(), file_name)
    config = getConfig(file_path)
    if root in config and branch in config[root]:
        return config[root][branch]
    else:
        log(f"Error retrieving value. {root} or {branch} not found in the configuration file.")

def setConfigValue(root, branch, value):
    file_name = 'pathogen-config.yaml'
    file_path = os.path.join(os.getcwd(), file_name)
    config = getConfig(file_path)
    if root in config and branch in config[root]:
        config[root][branch] = value
        saveConfig(file_path, config)
    else:
        log(f"Error setting value. {root} or {branch} not found in the configuration file.")

def log(log):
    if getConfigValue('logging', 'logging-enabled'):
        print(log)