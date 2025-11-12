"""
Author: Antonello Paolino
Date: 2025-05-07
Description:    This code uses the pyFluent packages to run iRonCub automatic CFD
                simulations starting from previously defined case files.
"""

from pathlib import Path
import toml

# src modules
import src.log as log
import src.solver as sol


def main():
    # INITIALIZE DIRECTORIES
    root = Path(__file__).parents[0]
    (
        cas_dir,
        residuals_dir,
        contours_dir,
        node_dir,
        cell_dir,
        aero_coefs_dir,
        log_dir,
        out_dir,
    ) = sol.initialize_directories(root)
    # SET CONFIGURATION OPTIONS
    options = toml.load(root / "config" / "config.toml")
    # Create the log files
    log_file, err_file = sol.initialize_log_files(log_dir)
    # Print info
    log.print_info(f"{residuals_dir.stem} path: {residuals_dir}", log_file)
    log.print_info(f"{contours_dir.stem} path: {contours_dir}", log_file)
    log.print_info(f"{node_dir.stem} path: {node_dir}", log_file)
    log.print_info(f"{cell_dir.stem} path: {cell_dir}", log_file)

    # Get the joint configuration names and the pitch and yaw angles
    configs = sol.get_joint_config_names(root / "input" / "joint-config.csv")
    pitch_angles = sol.get_angles(root / "input" / "pitch-angles.csv")
    yaw_angles = sol.get_angles(root / "input" / "yaw-angles.csv")

    # Start the automatic process
    for config in configs:

        sol.initialize_output_coefficients_file(config, options, aero_coefs_dir)

        for yaw in yaw_angles:
            # Start Fluent solver
            log.print_info(f"Starting pyfluent session, yaw={yaw}.", log_file)
            solver = sol.Solution(options, log_dir, log_file, err_file)
            solver.get_output_coefficients_list(config, aero_coefs_dir)

            temp_pitch_angles = pitch_angles.copy()
            while len(temp_pitch_angles) > 0:
                pitch = temp_pitch_angles.pop(0)

                try:
                    # Set up simulation
                    solver.load_case(config, cas_dir)
                    solver.rotate_mesh(pitch, yaw)
                    solver.set_boundary_conditions()
                    solver.initialize_solution()
                    # Run simulation
                    solver.run_simulation()
                    # Post-process the solution
                    # solver.write_residuals(config, pitch, yaw, residuals_dir) # TODO: gets stuck (maybe try with newer pyfluent version)
                    solver.export_surface_data(config, pitch, yaw, cell_dir, node_dir)
                    solver.compute_output_coefs(config, pitch, yaw)

                    # Print success message
                    log.print_success(
                        f"{config}, alpha={pitch}, beta={yaw}: Success!", log_file
                    )

                except Exception as error:
                    log.print_err(
                        f"{config}, alpha={pitch}, beta={yaw} failed: {error}",
                        log_file,
                        err_file,
                    )
                    log.cleanup_files_failed_sim(config, pitch, yaw, out_dir)
                    solver.close()
                    log.rename_log_file(config, yaw)
                    # Reinitialize the next iteration with the same pitch angle
                    solver = sol.Solution(options, log_dir, log_file, err_file)
                    solver.get_output_coefficients_list(config, aero_coefs_dir)
                    temp_pitch_angles.insert(0, pitch)
                    continue

            # Close Fluent Solver Session
            solver.close()
            log.rename_log_file(config, yaw)
            log.print_success(f"{config} iterations completed!", log_file)

    # Close the process
    log.print_success("Automatic CFD process completed successfully!", log_file)


if __name__ == "__main__":
    main()
