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


# Function to get the joint configuration names from the joint configuration file
def getJointConfigNames(jointConfigFilePath):
    with open(str(jointConfigFilePath), "r") as jointConfigCSV:
        jointConfigFile = jointConfigCSV.readlines()
        jointConfigNames = []
        for jointConfig in jointConfigFile:
            temp = jointConfig[:-1].split(",")
            jointConfigNames.append(temp[0])

    return jointConfigNames


# Function to clean files and directories in a directory except the ones with the allowed extensions
def cleanFilesExceptExtension(directory, allowedExtensions):
    if isinstance(
        allowedExtensions, str
    ):  # Convert to list if single string is provided
        allowedExtensions = [allowedExtensions]
    directoryPath = pathlib.Path(directory)
    for item in directoryPath.glob("**/*"):
        if item.is_file() and item.suffix not in allowedExtensions:
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
