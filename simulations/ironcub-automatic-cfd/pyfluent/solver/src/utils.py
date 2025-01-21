"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This file encloses some utility functions used in the main script.
"""

# Import libraries
import os
import pathlib
import shutil


# ANSI color codes class
class colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"


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
def get_joint_config_names(joint_config_path):
    with open(str(joint_config_path), "r") as joint_config_csv:
        joint_config_file = joint_config_csv.readlines()
        joint_config_names = []
        for joint_config in joint_config_file:
            temp = joint_config[:-1].split(",")
            joint_config_names.append(temp[0])
    return joint_config_names


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
