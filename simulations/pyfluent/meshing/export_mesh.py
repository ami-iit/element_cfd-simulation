"""
Author: Antonello Paolino
Date: 2025-06-25
Description:    This code uses the pyFluent packages to load a mesh in binary
                format and export it in ascii format to be used for post-
                processing (e.g. creating mesh graphs).
"""

from pathlib import Path
import ansys.fluent.core as pyfluent
import os
import sys

from src import log
from src import init
from src.constants import Const

CORE_NUM = 12


class Mesh:
    def __init__(self):
        mpi_option = "-mpi=openmpi" if os.name == "posix" else ""
        self.meshing = pyfluent.launch_fluent(
            mode="meshing",
            precision="double",
            product_version="25.1.0",
            dimension=3,
            processor_count=CORE_NUM,
            gpu=False,
            start_transcript=False,
            cwd=str(Const.log_dir),
            additional_arguments=mpi_option,
        )
        self.wf = self.meshing.workflow
        self.tui = self.meshing.tui

    def read_mesh(self, config_name):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = Const.msh_dir / msh_file_name
        self.tui.file.read_mesh(str(msh_file_path))

    def export_boundary_mesh(self, surface_list, config_name):
        ascii_dir = Const.msh_dir.parent / "ascii"
        ascii_dir.mkdir(parents=True, exist_ok=True)
        print(f"Exporting boundary mesh files to {ascii_dir}")
        for surface in surface_list:
            filename = ascii_dir / f"{config_name}-{surface}.msh"
            self.tui.file.write_boundaries(str(filename), surface)

    def close(self):
        self.meshing.exit()


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

    # Get the joint configuration names
    config_names = init.get_joint_config_names()
    def_surface_list = init.get_surface_list()

    # Start the automatic process
    for config_name in config_names:

        try:
            # WRITE BOUNDARIES
            # Start Fluent meshing
            mesh = Mesh()
            # Read generated mesh
            mesh.read_mesh(config_name)
            # Export boundary mesh files
            mesh.export_boundary_mesh(def_surface_list, config_name)
            # Close Fluent meshing
            mesh.close()

            # Close Fluent and clean up debug files
            log.print_success(f"{config_name} mesh converted to ascii.")

        except Exception as error:
            try:
                mesh.close()
            except Exception as e:
                log.print_err(f"Error closing mesh: {e}")

            # Print error and pass to next iteration
            log.print_err(f"{config_name} mesh conversion failed: {error}")
            pass

        log.clean_files_except_ext(Const.msh_dir, [".h5", ".msh"])
        log.clean_files_except_ext(Const.dlm_dir, [".dlm"])
        log.clean_files_except_ext(Const.log_dir, [".log", ".err"])
        log.clean_files_except_ext(Const.cas_dir, [".h5", ".cas"])

    # Close the process
    log.print_success("Mesh conversion completed!")


if __name__ == "__main__":
    main()
