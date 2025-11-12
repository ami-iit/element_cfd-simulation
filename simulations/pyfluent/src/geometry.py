"""
Author: Antonello Paolino
Date: 2025-10-24
Description:    Geometry module for robot configuration change
                using pyAnsys geometry package.
"""

from ansys.geometry.core import launch_modeler_with_discovery
from ansys.geometry.core.misc.measurements import UNITS, DEFAULT_UNITS
from ansys.geometry.core.math import Point3D, UNITVECTOR3D_X
from datetime import datetime

# src modules
import src.log as log

# set default units for geometry measurements
DEFAULT_UNITS.LENGTH = UNITS.m
DEFAULT_UNITS.ANGLE = UNITS.deg


def initialize_directories(root):
    in_dir = root / "input"
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    geom_dir = out_dir / "geometry" / "geometries"
    geom_dir.mkdir(parents=True, exist_ok=True)
    log_dir = out_dir / "geometry" / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return in_dir, geom_dir, log_dir


def initialize_log_files(log_dir):
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    log_file = log_dir / f"geom-{datetime_str}.log"
    log_file.touch(exist_ok=True)
    err_file = log_dir / f"geom-{datetime_str}.err"
    err_file.touch(exist_ok=True)
    return log_file, err_file


class Geometry:
    def __init__(self, options, log_file=None, err_file=None):
        self.modeler = launch_modeler_with_discovery(
            hidden=not options["general"]["show_gui"]
        )
        self.log_file = log_file
        self.err_file = err_file
        self.options = options["geometry"]

    def import_geometry(self, geom_file_path):
        log.print_info(f"Importing geometry from {geom_file_path}", self.log_file)
        self.design = self.modeler.open_file(geom_file_path)
        self.robot = self.design.components[1]
        self.bodies = self.robot.get_all_bodies()
        self.frames = {csys.name: csys.frame for csys in self.robot.coordinate_systems}

    def set_joint_configuration(self, joint_pos):
        log.print_info(f"Setting joint configuration: {joint_pos}", self.log_file)
        # Left arm joints
        la_names = self.options["la_links"]
        f_names = self.options["la_frames"]
        angles = [joint_pos[6], joint_pos[5], joint_pos[4] - 5, joint_pos[3]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in la_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])
        # Right arm joints
        ra_names = self.options["ra_links"]
        f_names = self.options["ra_frames"]
        angles = [joint_pos[10], joint_pos[9], joint_pos[8] - 5, joint_pos[7]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ra_names[: i + 1]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])
        # Torso joints
        b_names = self.options["b_links"]  # body names
        ub_names = la_names + ra_names + b_names  # upper body names
        f_names = self.options["b_frames"]
        angles = [joint_pos[2], joint_pos[0], joint_pos[1]]
        for i, f_name in enumerate(f_names):
            n = len(ub_names)
            part = [body for body in self.bodies if body.name in ub_names[: n + i - 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])
        # Left leg
        ll_names = self.options["ll_links"]
        f_names = self.options["ll_frames"]
        angles = [joint_pos[14], joint_pos[13], joint_pos[12], joint_pos[11]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in ll_names[: i + 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])
        # Right leg
        rl_names = self.options["rl_links"]
        f_names = self.options["rl_frames"]
        angles = [joint_pos[18], joint_pos[17], joint_pos[16], joint_pos[15]]
        for i, f_name in enumerate(f_names):
            part = [body for body in self.bodies if body.name in rl_names[: i + 2]]
            frame = self.frames[f_name]
            for body in part:
                body.rotate(frame.origin, frame.direction_z, angles[i])
        # Set the robot at alpha=0 beta=0
        for body in self.bodies:
            body.rotate(Point3D([0, 0, 0]), UNITVECTOR3D_X, 90.0)

    def create_named_selections(self):
        for body in self.bodies:
            self.design.create_named_selection(name=body.name, faces=body.faces)

    def export_geometry_to_pmdb_format(self, export_path):
        export_file = self.design.export_to_pmdb(export_path)
        log.print_info(f"Geometry exported to: {export_file}", self.log_file)

    def close_geometry(self):
        self.design.close()
        log.print_info("Design closed.", self.log_file)

    def close_modeler(self):
        self.modeler.close()
        log.print_info("Modeler closed.", self.log_file)
