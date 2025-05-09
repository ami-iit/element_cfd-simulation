"""
Author: Antonello Paolino
Date: 2025-05-07
Description:    This code uses the pyFluent packages to run iRonCub automatic CFD
                simulations starting from previously defined case files.
"""

from pathlib import Path
import sys

from src import log
from src import init
from src.solve import Solver
from src.constants import Const


def main():
    # SET CONFIGURATION OPTIONS
    # Get default values
    default_values = Const.get_default_values()
    # Read configuration file
    options = init.read_config_file(sys.argv)
    # Set constant values from options dictionary
    Const.set_val_from_options(options)
    # Print configuration options
    init.print_options(options, default_values)

    # INITIALIZE DIRECTORIES
    root = Path(__file__).parents[0]
    parent = Path(__file__).parents[1]
    init.initialize_directories(root, parent)
    # Create the log files
    init.initialize_log_files()
    # Print info
    log.print_info(f"{Const.residuals_dir.stem} path: {Const.residuals_dir}")
    log.print_info(f"{Const.contours_dir.stem} path: {Const.contours_dir}")
    log.print_info(f"{Const.node_dtbs_dir.stem} path: {Const.node_dtbs_dir}")
    log.print_info(f"{Const.cell_dtbs_dir.stem} path: {Const.cell_dtbs_dir}")

    # Get the joint configuration names
    config_names = init.get_joint_config_names()
    pitch_angles = init.get_pitch_angles()
    yaw_angles = init.get_yaw_angles()
    def_surface_list = init.get_surface_list()

    # Start the automatic process
    for config in config_names:

        init.initialize_output_coefficients_file(config, def_surface_list)

        for yaw in yaw_angles:
            # Start Fluent solver
            log.print_info(f"Starting pyfluent session, yaw={yaw}.")
            solver = Solver()
            solver.get_output_coefficients_list(config)

            for pitch in pitch_angles:
                try:
                    # Set up simulation
                    solver.load_case(config)
                    solver.rotate_mesh(pitch, yaw)
                    solver.set_boundary_conditions()
                    solver.initialize_solution()
                    # Run simulation
                    solver.run_simulation()
                    # Post-process the solution
                    solver.compute_output_coefs(config, pitch, yaw)
                    solver.export_surface_data(config, pitch, yaw, def_surface_list)
                    # Print success message
                    log.print_success(f"{config}, alpha={pitch}, beta={yaw}: Success!")

                except Exception as error:
                    log.cleanup_files_failed_sim(config, pitch, yaw)
                    log.print_err(
                        f"{config}, alpha={pitch}, beta={yaw} failed: {error}"
                    )
                    pass

            # Close Fluent Solver Session
            solver.close()
            log.rename_log_file(config, yaw)
            log.print_success(f"{config} iterations completed!")

    # Close the process
    log.print_success("Automatic CFD process completed successfully!")


if __name__ == "__main__":
    main()
