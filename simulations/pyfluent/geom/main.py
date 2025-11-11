"""
Author: Antonello Paolino
Date: 2025-05-12
Description:    This code uses the pyAnsys geometry package to load the robot
                CAD model and modify the joint configuration.
"""

import numpy as np
from pathlib import Path
from src.geometry import Geometry


SHOW_GUI = False


def main():
    # get input files
    root = Path(__file__).parents[0]
    joint_config_file_path = root / "config" / "joint-config.csv"
    geom_config_file_path = root / "config" / "geom.toml"
    geom_file_path = root / "config" / "geom.dsco"

    # create output directory
    out_dir = root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Initialize modeler
    geom = Geometry(hidden_gui=not SHOW_GUI)

    # Get all joint configurations
    configs = np.genfromtxt(joint_config_file_path, delimiter=",", dtype=str)

    for config in configs:
        # get configuration name and joint positions
        config_name = str(config[0])
        joint_pos = config[1:].astype(float)
        # Launch the modeler to operate on joint configuration
        geom.import_geometry(geom_file_path, geom_config_file_path)
        # geom.robot.plot()  # plot initial robot position
        geom.set_joint_configuration(joint_pos)
        # geom.robot.plot()  # plot modified robot position
        geom.export_geometry_to_pmdb_format(out_dir / f"{config_name}.pmdb")
        geom.close_geometry()
    # Close process
    geom.close_modeler()
    print("Process completed.")


if __name__ == "__main__":
    main()
