"""
Author: Antonello Paolino
Date: 2025-03-28
Description:    This code uses the pyFluent packages to generate a mesh and set up
                simulation parameters to perfom automatic CFD simulations starting
                from a given iRonCub CAD model.
"""

from pathlib import Path
import sys

from src import log
from src import init
from src.mesh import Mesh
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
    log.print_info(f"{Const.msh_dir.stem} path: {Const.msh_dir}")
    log.print_info(f"{Const.dlm_dir.stem} path: {Const.dlm_dir}")
    log.print_info(f"{Const.cas_dir.stem} path: {Const.cas_dir}")

    # Get the joint configuration names
    config_names = init.get_joint_config_names()
    def_surface_list = init.get_surface_list()

    # Start the automatic process
    for config_name in config_names:

        try:
            # WATERTIGHT WORKFLOW OPERATIONS
            # Start Fluent meshing
            log.print_info(f"Starting pyfluent session (1/3).")
            mesh = Mesh()
            # Initialize the workflow
            mesh.initialize_workflow()
            # Import geometry
            mesh.import_geometry(config_name)
            # Create surface mesh
            mesh.add_robot_local_sizings(def_surface_list)
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
            mesh.write_mesh(config_name)
            mesh.close()

            # WRITE BOUNDARIES
            # Start Fluent meshing
            log.print_info(f"Starting pyfluent session (2/3).")
            mesh = Mesh()
            # Read generated mesh
            mesh.read_mesh(config_name)
            # Export boundary mesh files
            mesh.export_boundary_mesh(def_surface_list, config_name)
            # Close Fluent meshing
            mesh.close()

            # SETUP CASE FILE FOR SIMULATIONS
            # Start Fluent solver
            log.print_info(f"Starting pyfluent session (3/3).")
            solver = Solver()
            # Read and check the mesh
            solver.read_mesh(config_name)
            # Modify zones and regions
            solver.modify_boundaries()
            # Simulation settings
            solver.set_viscous_model()
            solver.set_boundary_conditions()
            solver.set_methods()
            solver.create_report_definitions(def_surface_list)
            solver.create_contour_plane()
            solver.initialize_solution()
            # Write files
            solver.write_dual_mesh(def_surface_list, config_name)
            solver.write_case(config_name)
            # Close Fluent solver
            solver.close()

            # Close Fluent and clean up debug files
            log.print_success(f"{config_name} mesh generated.")

        except Exception as error:
            try:
                mesh.close()
            except Exception as e:
                log.print_err(f"Error closing mesh: {e}")
            try:
                solver.close()
            except Exception as e:
                log.print_err(f"Error closing solver: {e}")

            # Print error and pass to next iteration
            log.print_err(f"{config_name} mesh generation failed: {error}")
            pass

        log.clean_files_except_ext(Const.msh_dir, [".h5", ".msh"])
        log.clean_files_except_ext(Const.dlm_dir, [".dlm"])
        log.clean_files_except_ext(Const.log_dir, [".log", ".err"])
        log.clean_files_except_ext(Const.cas_dir, [".h5", ".cas"])

    # Close the process
    log.print_success("Meshing routine completed!")


if __name__ == "__main__":
    main()
