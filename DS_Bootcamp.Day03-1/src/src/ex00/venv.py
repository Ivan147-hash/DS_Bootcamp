import os

def get_venv():
    venv_path = os.environ["VIRTUAL_ENV"]
    print(f"Your current virtual env is {venv_path}")

if __name__ == '__main__':
    get_venv()