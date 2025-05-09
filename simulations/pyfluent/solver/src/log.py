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


def cleanup_files_failed_sim(config_name, pitch_angle, yaw_angle):
    out_dirs = [
        Const.residuals_dir,
        Const.contours_dir,
        Const.node_dtbs_dir,
        Const.cell_dtbs_dir,
    ]
    for out_dir in out_dirs:
        dtbs_file = f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}*.dtbs"
        # Remove file if it exists
        for file in out_dir.rglob(dtbs_file):
            if file.is_file():
                file.unlink()


def rename_log_file(config, yaw_angle):
    file_name = "nohup.out"
    file_path = Const.log_dir / file_name
    new_file_name = f"nohup-{config}-{int(yaw_angle)}.out"
    new_file_path = Const.log_dir / new_file_name
    # Rename file if it exists
    if file_path.is_file():
        shutil.move(str(file_path), str(new_file_path))
        print_info(f"Log file renamed to {new_file_name}.")
    else:
        print_err(f"Log file {file_name} not found.")
