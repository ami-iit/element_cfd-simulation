import shutil
from pathlib import Path
from datetime import datetime
from src.constants import Const


def print_info(message):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Info] [{time}] "
    print("\033[96m", pref, message, "\033[0m")
    with open(str(Const.log_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_err(message):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Error] [{time}] "
    print("\033[91m", pref, message, "\033[0m")
    with open(str(Const.log_file), "a") as f:
        f.writelines(pref + message + "\n")
    with open(str(Const.err_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_warn(message):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Warning] [{time}] "
    print("\033[93m", pref, message, "\033[0m")
    with open(str(Const.log_file), "a") as f:
        f.writelines(pref + message + "\n")
    with open(str(Const.err_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_success(message):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Success] [{time}] "
    print("\033[92m", pref, message, "\033[0m")
    with open(str(Const.log_file), "a") as f:
        f.writelines(pref + message + "\n")


def clean_files_except_ext(directory, allowed_ext):
    if isinstance(allowed_ext, str):
        allowed_ext = [allowed_ext]
    dir_path = Path(directory)
    for item in dir_path.glob("**/*"):
        if item.is_file() and item.suffix not in allowed_ext:
            try:
                item.unlink()
                print(f"Deleted file: {item}")
            except Exception as e:
                print(f"Failed to delete file: {item}: {e}")
        elif item.is_dir():
            try:
                shutil.rmtree(item)
                print(f"Deleted directory and its contents: {item}")
            except Exception as e:
                print(f"Failed to delete directory: {item}: {e}")
