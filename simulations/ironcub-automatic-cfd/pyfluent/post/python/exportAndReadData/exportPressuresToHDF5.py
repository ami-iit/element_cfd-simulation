import h5py
import numpy as np
import pathlib
import os
import glob

# Paths
rootPath = pathlib.Path(__file__).parents[1]
pressureDir = rootPath / "data" / "pressures"

# Get the list of files in the pressure directory
filePaths = glob.glob(str(pressureDir) + "/*.prs")
fileList = [os.path.basename(path) for path in filePaths]

# Get the list of joint configurations from the list of files
jointConfigNames = list(set([fileName.split("-")[0] for fileName in fileList]))

# Loop over the joint configurations
for jointConfigName in jointConfigNames:

    # Initialize the list of samples
    samples = []

    # Get the list of files relative to the current joint configuration
    jointConfigFileList = [
        fileName for fileName in fileList if fileName.startswith(f"{jointConfigName}-")
    ]

    # Get the list of pitch and yaw angles
    pitchAngleList = [
        fileName[len(jointConfigName) + 1 :].split("-")[0]
        for fileName in jointConfigFileList
    ]
    yawAngleList = [
        fileName[len(jointConfigName) + 1 :].split("-")[1]
        for fileName in jointConfigFileList
    ]

    # Create a list of unique tuples with the pitch and yaw angles
    pitchYawAnglePairs = {(x, y) for x, y in zip(pitchAngleList, yawAngleList)}

    pitchAngles = []
    yawAngles = []
    pressureData = []

    for pitchAngle, yawAngle in pitchYawAnglePairs:

        # Initialize the list of pressure files and the list of surfaces
        pressureFileList = []
        surfaceList = []
        pressureSampleData = []

        findString = f"{jointConfigName}-{pitchAngle}-{yawAngle}-"

        for fileName in os.listdir(pressureDir):

            if fileName.startswith(findString):

                pressureFileList.append(fileName)
                surfaceName = fileName[len(findString) : -4]
                surfaceList.append(surfaceName)
                with open(str(pressureDir / fileName), "r") as prsFile:
                    dataFile = prsFile.readlines()
                    dataListStr = [dataRow.split() for dataRow in dataFile]
                    surfacePressureData = [
                        [float(dataStr) for dataStr in dataListRow[1:]]
                        for dataListRow in dataListStr[1:]
                    ]

                pressureSampleData.append(surfacePressureData)

        pitchAngles.append(pitchAngle)
        yawAngles.append(yawAngle)
        pressureData.append(pressureSampleData)

    # Save the pressure data and the surfaceList to an HDF5 file
    hdf5FilePath = pressureDir / f"pressures_{jointConfigName}.hdf5"

    # Remove the file if it already exists
    if os.path.exists(hdf5FilePath):
        os.remove(hdf5FilePath)

    with h5py.File(hdf5FilePath, "w") as hdf5File:
        hdf5File.create_dataset("pitchAngles", data=pitchAngles)
        hdf5File.create_dataset("yawAngles", data=yawAngles)
        hdf5File.create_dataset("surfaceList", data=surfaceList)

        for surfaceIndex, surfaceName in enumerate(surfaceList):
            surfaceDataList = []

            for sampleIndex, sample in enumerate(pressureData):
                surfaceDataList.append(pressureData[sampleIndex][surfaceIndex])

            hdf5File.create_dataset(surfaceName, data=surfaceDataList)
