"""
Author: Antonello Paolino
Date: 2025-05-12
Description:    This code uses the pyAnsys geometry package to load the robot
                CAD model and modify the joint configuration.
"""

import numpy as np
import toml
from pathlib import Path

# src modules
import src.geometry as geom
import src.log as log


def main():
    # get input files
    root = Path(__file__).parents[0]
    input_dir, geom_dir, log_dir = geom.initialize_directories(root)

    # Create the log files
    log_file, err_file = geom.initialize_log_files(log_dir)

    # Define input files
    options = toml.load(root / "config" / "config.toml")
    joint_config_file_path = input_dir / "joint-config.csv"
    geom_file_path = input_dir / "geometry.dsco"

    # Print info
    log.print_info(f"{input_dir.stem} path: {input_dir}", log_file)
    log.print_info(f"{geom_dir.stem} path: {geom_dir}", log_file)
    log.print_info(f"{log_dir.stem} path: {log_dir}", log_file)

    # Initialize modeler
    geometry = geom.Geometry(options, log_file, err_file)

    # Get all joint configurations
    configs = np.genfromtxt(joint_config_file_path, delimiter=",", dtype=str)

    for config in configs:
        # get configuration name and joint positions
        config_name = str(config[0])
        joint_pos = config[1:].astype(float)
        # Launch the modeler to operate on joint configuration
        geometry.import_geometry(geom_file_path)
        # geometry.robot.plot()  # plot initial robot position
        geometry.set_joint_configuration(joint_pos)
        # geometry.robot.plot()  # plot modified robot position
        geometry.create_named_selections()
        geometry.export_geometry_to_pmdb_format(geom_dir / f"{config_name}")
        geometry.close_geometry()
    # Close process
    geometry.close_modeler()
    log.print_info("Process completed.", log_file)


if __name__ == "__main__":
    main()
