"""
Author: Antonello Paolino
Date: 2025-05-12
Description:    This code uses the pyAnsys geometry package to load the robot
                CAD model and modify the joint configuration.
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

from src.geometry import Geometry

PLOT_ROBOT = False
DEFAULT_UNITS.LENGTH = UNITS.m
DEFAULT_UNITS.ANGLE = UNITS.deg


def main():
    # get input files
    root = Path(__file__).parents[0]
    config_file_path = root / "src" / "jointConfig-mk3.csv"
    geom_file_path = root / "src" / "ironcub-mk3-fluid.dsco"

    # create output directory
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Initialize modeler
    geom = Geometry(hidden_gui=True)

    # Get all configs
    configs = np.genfromtxt(config_file_path, delimiter=",", dtype=str)

    for config in configs:
        # get configuration name and joint positions
        config_name = str(config[0])
        joint_pos = config[1:].astype(float)
        # Launch the modeler to operate on joint configuration
        geom.import_geometry(geom_file_path)
        geom.robot.plot() if PLOT_ROBOT else None  # plot original robot position
        geom.set_joint_configuration(joint_pos)
        geom.robot.plot() if PLOT_ROBOT else None  # plot modified robot position
        geom.export_geometry_to_pmdb_format(out_dir / f"{config_name}.pmdb")
        geom.close_geometry()
    # Close process
    geom.close_modeler()
    print("Process completed.")


if __name__ == "__main__":
    main()
