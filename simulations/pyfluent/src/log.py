import shutil
from pathlib import Path
from datetime import datetime


def print_info(message, log_file):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Info] [{time}] "
    print("\033[96m", pref, message, "\033[0m")
    with open(str(log_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_err(message, log_file, err_file):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Error] [{time}] "
    print("\033[91m", pref, message, "\033[0m")
    with open(str(log_file), "a") as f:
        f.writelines(pref + message + "\n")
    with open(str(err_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_warn(message, log_file, err_file):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Warning] [{time}] "
    print("\033[93m", pref, message, "\033[0m")
    with open(str(log_file), "a") as f:
        f.writelines(pref + message + "\n")
    with open(str(err_file), "a") as f:
        f.writelines(pref + message + "\n")


def print_success(message, log_file):
    time = datetime.now().strftime("%H:%M:%S")
    pref = f"[Success] [{time}] "
    print("\033[92m", pref, message, "\033[0m")
    with open(str(log_file), "a") as f:
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


def cleanup_files_failed_sim(config_name, pitch_angle, yaw_angle, out_dir):
    # get out_dir subdirectories
    out_dirs = out_dir.iterdir()
    for out_dir in out_dirs:
        file = f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}*"
        # Remove file if it exists
        for file in out_dir.rglob(file):
            if file.is_file():
                file.unlink()


def rename_log_file(config, yaw_angle, log_dir, log_file, err_file):
    file_name = "nohup.out"
    file_path = log_dir / file_name
    file_number = 0
    # Check if the file already exists with a different name
    new_file_name = f"nohup-{config}-{int(yaw_angle)}-{file_number}.out"
    while (log_dir / new_file_name).is_file():
        file_number += 1
        new_file_name = f"nohup-{config}-{int(yaw_angle)}-{file_number}.out"
    new_file_path = log_dir / new_file_name
    # Rename file if it exists
    if file_path.is_file():
        shutil.move(str(file_path), str(new_file_path))
        print_info(f"Log file renamed to {new_file_name}.", log_file)
    else:
        print_err(f"Log file {file_name} not found.", log_file, err_file)
