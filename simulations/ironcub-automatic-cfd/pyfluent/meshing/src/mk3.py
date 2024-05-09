# This file contains the iRonCub-Mk3 specific parameters for the meshing process

# Surface Mesh Size Function
surfaceMeshSizeFunction = "Curvature & Proximity"

# Define the list of ironcub surfaces
ironcubSurfacesList = [
    "ironcub_head",
    "ironcub_left_back_turbine",
    "ironcub_right_back_turbine",
    "ironcub_left_arm",
    "ironcub_left_arm_pitch",
    "ironcub_left_arm_roll",
    "ironcub_left_turbine",
    "ironcub_left_leg_lower",
    "ironcub_left_leg_pitch",
    "ironcub_left_leg_yaw",
    "ironcub_left_leg_upper",
    "ironcub_right_arm",
    "ironcub_right_arm_pitch",
    "ironcub_right_arm_roll",
    "ironcub_right_turbine",
    "ironcub_right_leg_lower",
    "ironcub_right_leg_pitch",
    "ironcub_right_leg_yaw",
    "ironcub_right_leg_upper",
    "ironcub_root_link",
    "ironcub_torso",
    "ironcub_torso_pitch",
    "ironcub_torso_roll",
]

# Define the surfaces skiplist (enclosed in the reports of the mergelist)
surfaceSkipList = [
    "ironcub_left_arm_pitch",
    "ironcub_left_arm_roll",
    "ironcub_right_arm_pitch",
    "ironcub_right_arm_roll",
    "ironcub_left_leg_pitch",
    "ironcub_left_leg_yaw",
    "ironcub_right_leg_pitch",
    "ironcub_right_leg_yaw",
    "ironcub_torso_pitch",
    "ironcub_torso_roll",
]

# Define the surfaces mergelist
surfaceMergeList = [
    "ironcub_left_arm",
    "ironcub_left_arm",
    "ironcub_right_arm",
    "ironcub_right_arm",
    "ironcub_left_leg_upper",
    "ironcub_left_leg_lower",
    "ironcub_right_leg_upper",
    "ironcub_left_leg_lower",
    "ironcub_torso",
    "ironcub_root_link",
]