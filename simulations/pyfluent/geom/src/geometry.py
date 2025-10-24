"""
Author: Antonello Paolino
Date: 2025-10-24
Description:    Geometry module for robot configuration change
                using pyAnsys geometry package.
"""

import numpy as np
from pathlib import Path
from ansys.geometry.core import (
    launch_modeler,
    launch_modeler_with_discovery,
    launch_modeler_with_geometry_service,
)
from ansys.geometry.core.misc.measurements import Angle, UNITS, DEFAULT_UNITS
from ansys.geometry.core.plotting import GeometryPlotter
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math import Point3D, UNITVECTOR3D_X

DEFAULT_UNITS.LENGTH = UNITS.m
DEFAULT_UNITS.ANGLE = UNITS.deg


class Geometry:
    def __init__(self, hidden_gui=True):
        self.modeler = launch_modeler_with_discovery(hidden=hidden_gui)

    def import_geometry(self, geom_file_path):
        print(f"Importing geometry from {geom_file_path}")
        self.design = self.modeler.open_file(geom_file_path)
        self.robot = self.design.components[1]
        self.bodies = self.robot.get_all_bodies()
        self.frames = {csys.name: csys.frame for csys in self.robot.coordinate_systems}

    def set_joint_configuration(self, joint_pos):
        print(f"Setting joint configuration: {joint_pos}")
        # Left arm joints
        la_names = ["left-turbine", "left-arm", "left-arm-roll", "left-arm-pitch"]
        f_names = [
            "left-elbow-csys",
            "left-arm-yaw-csys",
            "left-arm-roll-csys",
            "left-arm-pitch-csys",
        ]
        angles = [joint_pos[6], joint_pos[5], joint_pos[4] - 5, joint_pos[3]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in la_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Right arm joints
        ra_names = ["right-turbine", "right-arm", "right-arm-roll", "right-arm-pitch"]
        f_names = [
            "right-elbow-csys",
            "right-arm-yaw-csys",
            "right-arm-roll-csys",
            "right-arm-pitch-csys",
        ]
        angles = [joint_pos[10], joint_pos[9], joint_pos[8] - 5, joint_pos[7]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ra_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Torso joints
        ub_names = (
            la_names
            + ra_names
            + [
                "head",
                "torso",
                "upper-jetpack",
                "lower-jetpack",
                "left-back-turbine",
                "right-back-turbine",
                "torso-pitch",
                "torso-roll",
            ]
        )
        f_names = [
            "torso-yaw-csys",
            "torso-pitch-csys",
            "torso-roll-csys",
        ]
        angles = [joint_pos[2], joint_pos[0], joint_pos[1]]
        for i, f_name in enumerate(f_names):
            n = len(ub_names)
            part = [body for body in self.bodies if body.name in ub_names[: n + i - 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Left leg
        ll_names = [
            "left-foot",
            "left-leg-lower",
            "left-leg-yaw",
            "left-leg-upper",
            "left-leg-pitch",
        ]
        f_names = [
            "left-knee-csys",
            "left-leg-yaw-csys",
            "left-leg-roll-csys",
            "left-leg-pitch-csys",
        ]
        angles = [joint_pos[14], joint_pos[13], joint_pos[12], joint_pos[11]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ll_names[: i + 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Right leg
        rl_names = [
            "right-foot",
            "right-leg-lower",
            "right-leg-yaw",
            "right-leg-upper",
            "right-leg-pitch",
        ]
        f_names = [
            "right-knee-csys",
            "right-leg-yaw-csys",
            "right-leg-roll-csys",
            "right-leg-pitch-csys",
        ]
        angles = [joint_pos[18], joint_pos[17], joint_pos[16], joint_pos[15]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in rl_names[: i + 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Set the robot at alpha=0 beta=0
        for body in self.bodies:
            body.rotate(Point3D([0, 0, 0]), UNITVECTOR3D_X, 90.0)

    def export_geometry_to_pmdb_format(self, export_path):
        self.design.export_to_pmdb(export_path)
        print(f"Geometry exported to {export_path}")

    def close_geometry(self):
        self.design.close()
        print("Design closed.")

    def close_modeler(self):
        self.modeler.close()
        print("Modeler closed.")
