"""
Author: Antonello Paolino
Date: 2025-03-28
Description:    This code uses the pyFluent packages to generate a mesh and set up
                simulation parameters to perfom automatic CFD simulations starting
                from a given iRonCub CAD model.
"""

from pathlib import Path
import toml

# src modules
import src.mesher as msh
import src.log as log
import src.solver as sol


def main():
    # INITIALIZE DIRECTORIES
    root = Path(__file__).parents[0]
    geom_dir, msh_dir, dlm_dir, cas_dir, log_dir = msh.initialize_directories(root)
    # Import configuration options
    options = toml.load(root / "config" / "config.toml")
    # Create the log files
    log_file, err_file = msh.initialize_log_files(log_dir)
    # Print info
    log.print_info(f"{msh_dir.stem} path: {msh_dir}", log_file)
    log.print_info(f"{dlm_dir.stem} path: {dlm_dir}", log_file)
    log.print_info(f"{cas_dir.stem} path: {cas_dir}", log_file)

    # Get the joint configuration names and the surface list
    configs = msh.get_joint_config_names(root / "input" / "joint-config.csv")

    # Start the automatic process
    for config in configs:

        try:
            # WATERTIGHT WORKFLOW OPERATIONS
            # Start Fluent meshing
            log.print_info(f"Starting pyfluent session (1/3).", log_file)
            mesh = msh.Mesh(options, log_dir, log_file, err_file)
            # Initialize the workflow
            mesh.initialize_workflow()
            # Import geometry
            mesh.import_geometry(config, geom_dir)
            # Create surface mesh
            mesh.add_robot_local_sizings()
            mesh.add_boundary_local_sizings()
            mesh.generate_surface_mesh()
            # Manage geometry
            mesh.describe_geometry()
            mesh.apply_share_topology()
            mesh.update_boundaries_and_regions()
            # Create volume mesh
            mesh.add_boundary_layer()
            mesh.generate_volume_mesh()
            mesh.improve_volume_mesh()
            # Check mesh, save mesh file and exit meshing mode
            mesh.check_mesh()
            mesh.write_mesh(config, msh_dir)
            mesh.close()

            # WRITE BOUNDARIES
            # Start Fluent meshing
            log.print_info(f"Starting pyfluent session (2/3).", log_file)
            mesh = msh.Mesh(options, log_dir, log_file, err_file)
            # Read generated mesh
            mesh.read_mesh(config, msh_dir)
            # Export boundary mesh files
            mesh.export_boundary_mesh(config, msh_dir)
            # Close Fluent meshing
            mesh.close()

            # SETUP CASE FILE FOR SIMULATIONS
            # Start Fluent solver
            log.print_info(f"Starting pyfluent session (3/3).", log_file)
            solver = sol.Solution(options, log_dir, log_file, err_file)
            # Read and check the mesh
            solver.read_mesh(config, msh_dir)
            # Modify zones and regions
            solver.modify_boundaries()
            # Simulation settings
            solver.set_viscous_model()
            solver.prepare_boundary_conditions()
            solver.set_methods()
            solver.create_report_definitions()
            solver.create_contour_plane()
            solver.initialize_solution()
            # Write files
            solver.write_dual_mesh(config, dlm_dir)
            solver.write_case(config, cas_dir)
            # Close Fluent solver
            solver.close()

            # Close Fluent and clean up debug files
            log.print_success(f"{config} mesh generated.", log_file)

        except Exception as error:
            try:
                mesh.close()
            except Exception as e:
                log.print_err(f"Error closing mesh: {e}", log_file, err_file)
            try:
                solver.close()
            except Exception as e:
                log.print_err(f"Error closing solver: {e}", log_file, err_file)

            # Print error and pass to next iteration
            log.print_err(
                f"{config} mesh generation failed: {error}", log_file, err_file
            )
            pass

        log.clean_files_except_ext(msh_dir, [".h5", ".msh"])
        log.clean_files_except_ext(dlm_dir, [".dlm"])
        log.clean_files_except_ext(log_dir, [".log", ".err"])
        log.clean_files_except_ext(cas_dir, [".h5", ".cas"])

    # Close the process
    log.print_success("Meshing routine completed!", log_file)


if __name__ == "__main__":
    main()
