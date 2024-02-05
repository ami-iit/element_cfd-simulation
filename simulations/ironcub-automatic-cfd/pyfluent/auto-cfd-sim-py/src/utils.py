# File containing some utility functions
import os
import pathlib
import shutil

# Function to get the list of angles from the angles file
def getAnglesList(anglesFilePath):
    with open(str(anglesFilePath), 'r') as angleCSV:
        angleFile    = angleCSV.readlines()
        angleString  = angleFile[0]
        angleListStr = angleString[:-1].split(',')
        angleList    = [float(angleStr) for angleStr in angleListStr]
        
    return angleList

# Function to get the output parameter list from the output parameter file
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


# Function to clean files and directories in a directory except the ones with the allowed extensions
def cleanFilesExceptExtension(directory, allowedExtensions):
    if isinstance(allowedExtensions, str):  # Convert to list if single string is provided
        allowedExtensions = [allowedExtensions]
    directoryPath = pathlib.Path(directory)
    for item in directoryPath.glob('**/*'):
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