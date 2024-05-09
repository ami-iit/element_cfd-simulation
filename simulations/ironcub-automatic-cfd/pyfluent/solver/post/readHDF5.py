import h5py
import numpy as np
import pathlib
import os

rootPath = pathlib.Path(__file__).parents[1]
pressureDir = rootPath / "data" / "pressures"

jointConfigName = "hovering"

hdf5FilePath = pressureDir / f"pressures_{jointConfigName}.hdf5"

data = {}

with h5py.File(hdf5FilePath, "r") as hdf5File:
    surfaceList_bytes = hdf5File["surfaceList"][:]
    pitchAngleList_bytes = hdf5File["pitchAngles"][:]
    yawAngleList_bytes = hdf5File["yawAngles"][:]

    # Decode byte strings to regular strings
    surfaceList = [s.decode("utf-8") for s in surfaceList_bytes]
    pitchAngles = np.array([float(p.decode("utf-8")) for p in pitchAngleList_bytes])
    yawAngles = np.array([float(y.decode("utf-8")) for y in yawAngleList_bytes])

    # Create a dictionary with the data
    jointConfigData = {}

    # Add the data to the dictionary
    jointConfigData["surfaceList"] = surfaceList
    jointConfigData["pitchAngles"] = pitchAngles
    jointConfigData["yawAngles"] = yawAngles
    for surfaceIndex, surfaceName in enumerate(surfaceList):
        jointConfigData[surfaceName] = hdf5File[surfaceName][:]

data[jointConfigName] = jointConfigData


print("controllino")
