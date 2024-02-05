# File containing some utility functions
import os
import pathlib
import shutil

# Function to get the input parameter list from the input parameter file
def getOutputParameterList(outputParamFilePath):
    with open(str(outputParamFilePath), 'r') as outputParamCSV:
        outputParameterFile   = outputParamCSV.readlines()
        outputParameterList   = outputParameterFile[0][:-1].split(',')
        outputParameterList   = outputParameterList[3:]
    
    return outputParameterList


# Function to get the joint configuration names from the joint configuration file
def getJointConfigNames(jointConfigFilePath):
    with open(str(jointConfigFilePath), 'r') as jointConfigCSV:
        jointConfigFile  = jointConfigCSV.readlines()
        jointConfigNames = []
        for jointConfig in jointConfigFile:
            temp = jointConfig[:-1].split(',')
            jointConfigNames.append(temp[0])
        
    return jointConfigNames


# Function to get the joint configuration names from the joint configuration file
def cleanFilesExceptExtension(directory, allowedExtension):
    directoryPath = pathlib.Path(directory)
    for item in directoryPath.glob('**/*'):
        if item.is_file() and not item.suffix == allowedExtension:
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