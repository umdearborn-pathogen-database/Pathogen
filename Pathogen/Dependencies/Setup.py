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
        'local-enabled': 'True',
        'local-file-name': 'pathogens.db',
        'remote-host': '127.0.0.1',
        'remote-port': '3306',
        'remote-database': 'pathogendb',
        'remote-username': 'admin',
        'remote-password': 'password'
    },
    'logging': {
        'logging-enabled': 'False',
        'logging-output': 'pathogens.log'
    },
    'options': {
        'remove-null-valued-spectra': 'False',
        'cancel-if-sum-is-zero': 'False',
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

def getConfigValueCasted(root, branch, cast_type):
    x = getConfigValue(root, branch)
    try:
        x = cast_type(x)
        return x
    except (ValueError, TypeError):
        print(f"Failed to correctly read in value '{x}' to {cast_type.__name__}")

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
    if getConfigValueCasted('logging', 'logging-enabled', eval):
        print(log)