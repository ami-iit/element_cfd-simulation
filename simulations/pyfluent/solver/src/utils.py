"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This file encloses some utility functions used in the main script.
"""

import pathlib
import shutil


# Function to print and log messages
def print_log(type, message, log_file):
    if type == "info":
        pref = ("\033[96m", "[Info] ")
    elif type == "error":
        pref = ("\033[91m", "[Error] ")
    elif type == "warning":
        pref = ("\033[93m", "[Warning] ")
    elif type == "success":
        pref = ("\033[92m", "[Success] ")
    print(pref[0], pref[1], message, "\033[0m")
    with open(str(log_file), "a") as f:
        f.writelines(pref[1] + message + "\n")


# Function to get the list of angles from the angles file
def get_angles_list(angles_file_path):
    with open(str(angles_file_path), "r") as angles_csv:
        angles_file = angles_csv.readlines()
        angles_string = angles_file[0]
        angles_str_list = angles_string[:-1].split(",")
        angles_list = [float(angle_str) for angle_str in angles_str_list]
    return angles_list


# Function to get the output parameter list from the output parameter file
def get_output_param_list(out_param_path):
    with open(str(out_param_path), "r") as out_param_csv:
        out_param_file = out_param_csv.readlines()
        out_param_list = out_param_file[0][:-1].split(",")
    return out_param_list[3:]


# Function to get the joint configuration names from the joint configuration file
def get_config_names(joint_config_file):
    with open(str(joint_config_file), "r") as f:
        config_file = f.readlines()
        config_names = []
        for config_name in config_file:
            temp = config_name[:-1].split(",")
            config_names.append(temp[0])
    return config_names


# Function to clean files and directories in a directory except the ones with the allowed extensions
def clean_files_with_exception(directory, allowed_ext):
    if isinstance(allowed_ext, str):  # Convert to list if single string is provided
        allowed_ext = [allowed_ext]
    dir_path = pathlib.Path(directory)
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
