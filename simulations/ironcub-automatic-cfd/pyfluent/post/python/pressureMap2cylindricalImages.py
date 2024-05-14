from idyntree import bindings as idyntree
import os
import pathlib
import numpy as np

from iDynTreeWrappersModule import loadReducedModel

### External settings
robotName       = "iRonCub-Mk3"

## Set the path to the iRonCub component software
ironcubSoftwarePath = pathlib.Path(os.getenv("IRONCUB_COMPONENT_SOURCE_DIR"))

## Initialize parameters
jointList = ["torso_pitch","torso_roll","torso_yaw",
             "l_shoulder_pitch","l_shoulder_roll","l_shoulder_yaw","l_elbow",
             "r_shoulder_pitch","r_shoulder_roll","r_shoulder_yaw","r_elbow",
             "l_hip_pitch","l_hip_roll","l_hip_yaw","l_knee","l_ankle_pitch","l_ankle_roll",
             "r_hip_pitch","r_hip_roll","r_hip_yaw","r_knee","r_ankle_pitch","r_ankle_roll"]
baseLinkName = "root_link"
modelFilePath = ironcubSoftwarePath / "models" / f"{robotName}" / "iRonCub" / "robots" / f"{robotName}_Gazebo" / "model.urdf"
debugMode = False

## Assign state variables
basePose = np.array([[1,0,0,0],
                     [0,1,0,0],
                     [0,0,1,0],
                     [0,0,0,1]])
jointPos = np.zeros(len(jointList))
jointPos[0] = 0
jointVel = np.zeros_like(jointPos)
baseVel  = np.zeros(6)
gravAcc  = np.array([0,0,9.81])

# load robot model
kinDynModel = loadReducedModel(jointList,baseLinkName,str(modelFilePath),debugMode)

# set robot state
kinDynComp  = kinDynModel["kinDynComp"]
if kinDynComp.setRobotState(basePose, jointPos, baseVel, jointVel, gravAcc):
    print("[setRobotState]: robot state set correctly.")
else:
    print("[setRobotState]: error in setting robot state.")

# get the robot state
jointPos_iDynTree = idyntree.VectorDynSize(kinDynModel["NDOF"])
kinDynComp.getJointPos(jointPos_iDynTree)


# Visualization
viz = idyntree.Visualizer()

if viz.addModel(kinDynComp.model(), "viz1"):
    print("[initializeVisualizer]: model loaded in the visualizer.")
else:
    print("[initializeVisualizer]: unable to load the model in the visualizer.")

viz.camera().animator().enableMouseControl(True)

while viz.run():
    viz.draw()
    # input("press enter to continue")


print("fermoooo")

