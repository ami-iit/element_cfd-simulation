"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This code uses the pyFluent packages to generate a mesh and set up 
                simulation parameters to perfom automatic CFD simulations starting 
                from a given iRonCub CAD model.

This code is based on the example provided at the following link: 
                
https://github.com/ansys/pyfluent/tree/v0.19.2/examples/00-fluent
"""

import ansys.fluent.core as pyfluent
from datetime import datetime
import pathlib
import os

from src.utils import print_log, get_config_names, clean_files_except_ext

ROBOT_NAME = "ironcub-mk3"
CORE_NUM = 64
USE_GPU = False


def main():
    # Define the robot properties
    if ROBOT_NAME == "ironcub-mk1":
        import src.mk1 as robot
    elif ROBOT_NAME == "ironcub-mk3":
        import src.mk3 as robot

    # Set the MPI option for the WS
    mpi_option = "-mpi=openmpi" if os.name == "posix" else ""

    # Define code and sources directory paths
    root_dir = pathlib.Path(__file__).parents[0]
    parent_dir = pathlib.Path(__file__).parents[1]
    geom_dir = parent_dir / "geom" / ROBOT_NAME[-3:]
    src_dir = root_dir / "src"

    # Create the log directory and files
    log_dir = root_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    log_file = log_dir / f"{datetime_str}.log"
    log_file.touch(exist_ok=True)
    err_file = log_dir / f"{datetime_str}.err"
    err_file.touch(exist_ok=True)

    # Define output directories
    msh_dir = root_dir / "mesh" / ROBOT_NAME[-3:] / "msh"
    dlm_dir = root_dir / "mesh" / ROBOT_NAME[-3:] / "dlm"
    cas_dir = root_dir / "case" / ROBOT_NAME[-3:]

    # Create output directories if they do not exist
    msh_dir.mkdir(parents=True, exist_ok=True)
    print_log("info", f"{msh_dir.stem} path: {msh_dir}", log_file)
    dlm_dir.mkdir(parents=True, exist_ok=True)
    print_log("info", f"{dlm_dir.stem} path: {dlm_dir}", log_file)
    cas_dir.mkdir(parents=True, exist_ok=True)
    print_log("info", f"{cas_dir.stem} path: {cas_dir}", log_file)

    # Define input file path
    joint_config_file = src_dir / f"joint-config-{ROBOT_NAME[-3:]}.csv"

    # Load the joint configuration names from the files.
    config_names = get_config_names(joint_config_file)

    # Start the automatic process
    for config_name in config_names:

        # Define geometry file and path for current configuration
        geom_file = geom_dir / config_name / "Geom.scdoc"

        try:
            # Launch Fluent
            time = datetime.now().strftime("%H:%M:%S")
            print_log("info", f"[{time}] Starting pyfluent session (1/3).", log_file)
            meshing = pyfluent.launch_fluent(
                mode="meshing",
                precision="double",
                product_version="24.1.0",
                dimension=3,
                processor_count=CORE_NUM,
                gpu=USE_GPU,
                start_transcript=False,
                cwd=str(log_dir),
                additional_arguments=mpi_option,
            )

            # Watertight geometry meshing workflow
            meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

            # Import CAD and set length units
            import_geom = meshing.workflow.TaskObject["Import Geometry"]
            import_geom.Arguments.set_state(
                {
                    "FileName": str(geom_file),
                    "LengthUnit": "mm",
                }
            )
            import_geom.Execute()

            # Add local sizing
            local_sizing = meshing.workflow.TaskObject["Add Local Sizing"]
            local_sizing.Arguments.set_state(
                {
                    "AddChild": "yes",
                    "BOIControlName": "ironcub-sizing",
                    "BOIFaceLabelList": robot.surface_list,
                    "BOISize": 20,
                }
            )
            local_sizing.AddChildAndUpdate()
            local_sizing.Arguments.set_state(
                {
                    "AddChild": "yes",
                    "BOIControlName": "external-sizing",
                    "BOIFaceLabelList": ["inlet", "outlet"],
                    "BOISize": 2000,
                }
            )
            local_sizing.AddChildAndUpdate()

            # Generate surface mesh
            surface_mesh = meshing.workflow.TaskObject["Generate the Surface Mesh"]
            surface_mesh.Arguments.set_state(
                {
                    "CFDSurfaceMeshControls": {
                        "MaxSize": 4000,
                        "MinSize": 5,
                        "SizeFunctions": robot.surface_mesh_size_function,
                    },
                    "ExecuteShareTopology": "Yes",
                }
            )
            surface_mesh.Execute()

            # Describe geometry
            describe_geom = meshing.workflow.TaskObject["Describe Geometry"]
            describe_geom.UpdateChildTasks(SetupTypeChanged=False)
            describe_geom.Arguments.set_state(
                {
                    "SetupType": "The geometry consists of both fluid and solid regions and/or voids"
                }
            )
            describe_geom.UpdateChildTasks(SetupTypeChanged=True)
            describe_geom.Execute()

            # Apply Share Topology
            share_topology = meshing.workflow.TaskObject["Apply Share Topology"]
            share_topology.Arguments.set_state(
                {
                    "GapDistance": 2.5,
                    "ShareTopologyPreferences": {"Operation": "Join-Intersect"},
                }
            )
            share_topology.Execute()

            # Update boundaries and regions
            meshing.workflow.TaskObject["Update Boundaries"].Execute()
            meshing.workflow.TaskObject["Update Regions"].Execute()

            # Add boundary layers
            boundary_layer = meshing.workflow.TaskObject["Add Boundary Layers"]
            boundary_layer.Arguments.set_state(
                {
                    "LocalPrismPreferences": {
                        "Continuous": "Stair Step",
                        "ShowLocalPrismPreferences": False,
                    },
                    "NumberOfLayers": 5,
                }
            )
            boundary_layer.AddChildAndUpdate()

            # Generate and improve volume mesh
            volume_mesh = meshing.workflow.TaskObject["Generate the Volume Mesh"]
            volume_mesh.Arguments.set_state(
                {
                    "MeshSolidRegions": False,
                    "PrismPreferences": {"ShowPrismPreferences": False},
                    "VolumeFill": "poly-hexcore",
                    "VolumeFillControls": {
                        "HexMaxCellLength": 2560,
                        "HexMinCellLength": 40,
                        "PeelLayers": 2,
                    },
                    "VolumeMeshPreferences": {"ShowVolumeMeshPreferences": False},
                }
            )
            volume_mesh.Execute()
            volume_mesh.InsertNextTask(CommandName="ImproveVolumeMesh")
            improve_volume_mesh = meshing.workflow.TaskObject["Improve Volume Mesh"]
            improve_volume_mesh.Arguments.set_state(
                {
                    "CellQualityLimit": 0.15,
                    "QualityMethod": "Orthogonal",
                    "VMImprovePreferences": {
                        "ShowVMImprovePreferences": True,
                        "VIQualityIterations": 5,
                        "VIQualityMinAngle": 0,
                        "VIgnoreFeature": "yes",
                    },
                }
            )
            improve_volume_mesh.Execute()

            # Check mesh, save mesh file and exit meshing mode
            meshing.tui.mesh.check_mesh()
            msh_file_name = config_name + ".msh.h5"
            msh_file_path = msh_dir.parent / msh_file_name
            meshing.tui.file.write_mesh(str(msh_file_path))
            meshing.exit()

            # Re-launch Fluent in meshing mode to write boundaries
            time = datetime.now().strftime("%H:%M:%S")
            print_log("info", f"[{time}] Starting pyfluent session (2/3).", log_file)
            meshing = pyfluent.launch_fluent(
                mode="meshing",
                precision="double",
                product_version="24.1.0",
                dimension=3,
                processor_count=CORE_NUM,
                gpu=USE_GPU,
                start_transcript=False,
                cwd=str(log_dir),
                additional_arguments=mpi_option,
            )

            # Read generated mesh
            meshing.tui.file.read_mesh(str(msh_file_path))

            # Export boundary mesh files
            for surface in robot.surface_list:
                filename = msh_dir / f"{config_name}-{surface}.msh"
                meshing.tui.file.write_boundaries(str(filename), surface)

            # exit meshing mode
            meshing.exit()

            # Re-launch Fluent in solver mode
            time = datetime.now().strftime("%H:%M:%S")
            print_log("info", f"[{time}] Starting pyfluent session (3/3).", log_file)
            solver = pyfluent.launch_fluent(
                mode="solver",
                precision="double",
                product_version="24.1.0",
                dimension=3,
                processor_count=CORE_NUM,
                gpu=USE_GPU,
                start_transcript=False,
                cwd=str(log_dir),
                additional_arguments=mpi_option,
            )

            # Load and check the mesh
            solver.file.read_mesh(file_name=str(msh_file_path))
            solver.mesh.check()

            # Modify zones and regions
            solver.mesh.modify_zones.zone_type(
                zone_names=["outlet"], new_type="velocity-inlet"
            )
            solver.mesh.modify_zones.merge_zones(zone_names=["inlet", "outlet"])

            solver.solution.cell_registers["region_in"] = {}
            region_in = solver.solution.cell_registers["region_in"]
            region_in.type.option = "hexahedron"
            region_in.type.hexahedron.min_point = [-100, -100, -1]
            region_in.type.hexahedron.max_point = [100, 100, 100]

            # Simulation Setup
            # Set the viscous model to k-w sst
            viscous = solver.setup.models.viscous
            viscous.model = "k-omega"
            viscous.k_omega_model = "sst"

            # Boundary Conditions
            inlet = solver.setup.boundary_conditions.velocity_inlet["inlet"]
            inlet.momentum.velocity_specification_method = "Magnitude and Direction"
            inlet.momentum.velocity = 17.0
            inlet.momentum.flow_direction = [0.0, 0.0, -1.0]
            inlet.turbulence.turbulent_specification = "Intensity and Viscosity Ratio"
            inlet.turbulence.turbulent_intensity = 0.001
            inlet.turbulence.turbulent_viscosity_ratio_real = 0.01

            # Reference values (for non-dimensionalization)
            solver.setup.reference_values.velocity.set_state(
                inlet.momentum.velocity.value.get_state()
            )

            # Solver methods
            solver.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")
            solver.solution.methods.warped_face_gradient_correction.enable = True
            solver.solution.methods.warped_face_gradient_correction.mode = (
                "memory-saving"
            )
            solver.solution.methods.pseudo_time_method.formulation.coupled_solver = (
                "off"
            )
            for equation in solver.solution.monitor.residual.equations.keys():
                solver.solution.monitor.residual.equations[
                    equation
                ].check_convergence = False

            # Report Definitions
            # initialize ironcub cd, cl, cs reports
            solver.solution.report_definitions.drag["ironcub-cd"] = {}
            solver.solution.report_definitions.drag["ironcub-cl"] = {}
            solver.solution.report_definitions.drag["ironcub-cs"] = {}
            # define ironcub cd, cl, cs reports
            cd = solver.solution.report_definitions.drag["ironcub-cd"]
            cl = solver.solution.report_definitions.drag["ironcub-cl"]
            cs = solver.solution.report_definitions.drag["ironcub-cs"]
            # get the complete list of surfaces from cd report
            surface_list = cd.zones.allowed_values()
            # set ironcub-cd report
            cd.zones = surface_list
            cd.force_vector = [0, 0, -1]
            cd.average_over = 100
            # set ironcub-cl report
            cl.zones = surface_list
            cl.force_vector = [0, 1, 0]
            cl.average_over = 100
            # set ironcub-cs report
            cs.zones = surface_list
            cs.force_vector = [-1, 0, 0]
            cs.average_over = 100

            # define the reports for the ironcub surfaces
            for rep_surf in robot.surface_list:
                rep_def_name = rep_surf[8:]
                rep_def_name = rep_def_name.replace("_", "-")
                rep_surf_list = [rep_surf]
                # check for duplicates of the main report surface
                rep_surf_pref = rep_surf + ":"
                for surface in surface_list:
                    if rep_surf_pref in surface:
                        rep_surf_list.extend([surface])
                # define surface cd report
                solver.solution.report_definitions.drag[rep_def_name + "-cd"] = {}
                cd = solver.solution.report_definitions.drag[rep_def_name + "-cd"]
                cd.zones = rep_surf_list
                cd.force_vector = [0, 0, -1]
                cd.average_over = 100
                # define surface cl report
                solver.solution.report_definitions.drag[rep_def_name + "-cl"] = {}
                cl = solver.solution.report_definitions.drag[rep_def_name + "-cl"]
                cl.zones = rep_surf_list
                cl.force_vector = [0, 1, 0]
                cl.average_over = 100
                # define surface cs report
                solver.solution.report_definitions.drag[rep_def_name + "-cs"] = {}
                cs = solver.solution.report_definitions.drag[rep_def_name + "-cs"]
                cs.zones = rep_surf_list
                cs.force_vector = [-1, 0, 0]
                cs.average_over = 100

            # Contour Plane Defintions
            solver.results.surfaces.plane_surface.create("yz-plane")
            yz_plane = solver.results.surfaces.plane_surface["yz-plane"]
            yz_plane.method = "yz-plane"
            yz_plane.x = 0.0

            # Initialize flow field and save case file
            solver.solution.initialization.hybrid_initialize()
            cas_file_name = config_name + ".cas.h5"
            cas_file_path = cas_dir / cas_file_name
            solver.file.write(file_name=str(cas_file_path), file_type="case")

            # Export dual mesh dlm files
            cd_report = solver.solution.report_definitions.drag["ironcub-cd"]
            surface_list = cd_report.zones.allowed_values()
            for rep_surf in robot.surface_list:
                rep_surf_list = [rep_surf]
                rep_surf_pref = rep_surf + ":"
                for surface in surface_list:
                    if rep_surf_pref in surface:
                        rep_surf_list.extend([surface])
                dtbs_file_name = f"mesh-{config_name}-0-0-{rep_surf}.dlm"
                dtbs_file_path = str(dlm_dir / dtbs_file_name)
                solver.file.export.ascii(
                    file_name=dtbs_file_path,
                    surface_name_list=rep_surf_list,
                    delimiter="space",
                    cell_func_domain=["x-face-area", "y-face-area", "z-face-area"],
                    location="cell-center",
                )

            # Close Fluent and clean up debug files
            solver.exit()
            time = datetime.now().strftime("%H:%M:%S")
            print_log("success", f"[{time}] {config_name} mesh generated!", log_file)

        except Exception as error:
            meshing.exit()
            time = datetime.now().strftime("%H:%M:%S")
            message = f"[{time}] {config_name} mesh generation failed!"
            print_log("error", message, log_file)
            with open(str(err_file), "a") as f:
                f.writelines(message + "\n" + str(error) + "\n")
            pass

        clean_files_except_ext(msh_dir, [".h5", ".dtbs", ".msh"])
        clean_files_except_ext(log_dir, [".log", ".err", ".trn", ".bat"])

    # Close the process
    time = datetime.now().strftime("%H:%M:%S")
    print_log("success", f"[{time}] Meshing routine completed!", log_file)


if __name__ == "__main__":
    main()
