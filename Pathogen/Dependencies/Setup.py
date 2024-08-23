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