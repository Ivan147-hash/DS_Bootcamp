import os
import sys
import subprocess

def get_venv():
    try:
        venv_path = os.environ["VIRTUAL_ENV"].split("/")
        if venv_path[-1] == "rossiesh":
            return True
        else:
            print("Wrong environment")
    except KeyError:
        print("Wrong environment")

def install_lib(lib):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + lib)
    except subprocess.CalledProcessError as e:
        print(f"Installation error: {e}")

def chek_requirements(output_file):
    try:
        with open(output_file, 'w') as inf:
            subprocess.check_call([sys.executable, '-m', 'pip', 'freeze'], stdout=inf)
    except subprocess.CalledProcessError as e:
        print(f"Error getting list of libraries: {e}")

if __name__ == '__main__':
    if get_venv():
        libs = ['beautifulsoup4', 'pytest']
        install_lib(libs)
        chek_requirements('requirements.txt')
        os.system('pip freeze')
