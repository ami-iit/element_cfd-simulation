"""
Author: Antonello Paolino
Date: 2025-10-24
Description:    Geometry module for robot configuration change
                using pyAnsys geometry package.
"""

from ansys.geometry.core import launch_modeler_with_discovery
from ansys.geometry.core.misc.measurements import UNITS, DEFAULT_UNITS
from ansys.geometry.core.math import Point3D, UNITVECTOR3D_X
import toml

DEFAULT_UNITS.LENGTH = UNITS.m
DEFAULT_UNITS.ANGLE = UNITS.deg


class Geometry:
    def __init__(self, hidden_gui=True):
        self.modeler = launch_modeler_with_discovery(hidden=hidden_gui)

    def import_geometry(self, geom_file_path, config_file_path):
        print(f"Importing geometry from {geom_file_path}")
        self.design = self.modeler.open_file(geom_file_path)
        self.robot = self.design.components[1]
        self.bodies = self.robot.get_all_bodies()
        self.frames = {csys.name: csys.frame for csys in self.robot.coordinate_systems}
        self.config = toml.load(config_file_path)

    def set_joint_configuration(self, joint_pos):
        print(f"Setting joint configuration: {joint_pos}")
        # Left arm joints
        la_names = self.config["left_arm"]["links"]
        f_names = self.config["left_arm"]["frames"]
        angles = [joint_pos[6], joint_pos[5], joint_pos[4] - 5, joint_pos[3]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in la_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Right arm joints
        ra_names = self.config["right_arm"]["links"]
        f_names = self.config["right_arm"]["frames"]
        angles = [joint_pos[10], joint_pos[9], joint_pos[8] - 5, joint_pos[7]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ra_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Torso joints
        b_names = self.config["body"]["links"]  # body names
        ub_names = la_names + ra_names + b_names  # upper body names
        f_names = self.config["body"]["frames"]
        angles = [joint_pos[2], joint_pos[0], joint_pos[1]]
        for i, f_name in enumerate(f_names):
            n = len(ub_names)
            part = [body for body in self.bodies if body.name in ub_names[: n + i - 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Left leg
        ll_names = self.config["left_leg"]["links"]
        f_names = self.config["left_leg"]["frames"]
        angles = [joint_pos[14], joint_pos[13], joint_pos[12], joint_pos[11]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ll_names[: i + 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])

        # Right leg
        rl_names = self.config["right_leg"]["links"]
        f_names = self.config["right_leg"]["frames"]
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
