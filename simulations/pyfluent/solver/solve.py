"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This code uses the pyFluent packages to run iRonCub automatic CFD 
                simulations starting from properly defined case files.

This code is based on the examples provided at the following link: 
                
https://github.com/ansys/pyfluent/tree/v0.19.2/examples/00-fluent
"""

import ansys.fluent.core as pyfluent
from datetime import datetime
import numpy as np
import pathlib
import os

from src.utils import (
    print_log,
    get_angles_list,
    get_output_param_list,
    get_config_names,
)


ROBOT_NAME = "ironcub-mk3"
CORE_NUM = 64
USE_GPU = False
ITER_NUM = 1000


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
    src_dir = root_dir / "src"
    cas_dir = parent_dir / "meshing" / "case" / ROBOT_NAME[-3:]

    # Define file paths
    pitch_angles_file = src_dir / "pitch-angles.csv"
    yaw_angles_start_file = src_dir / "yaw-angles-start.csv"
    yaw_angles_file = src_dir / "yaw-angles.csv"
    joint_config_file = src_dir / f"joint-config-{ROBOT_NAME[-3:]}.csv"

    # Load parameters from files
    pitch_angle_list = get_angles_list(pitch_angles_file)
    yaw_angle_start_list = get_angles_list(yaw_angles_start_file)
    yaw_angle_list = get_angles_list(yaw_angles_file)
    config_names = get_config_names(joint_config_file)

    # Create the log directory and files
    log_dir = root_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    log_file = log_dir / f"{datetime_str}.log"
    log_file.touch(exist_ok=True)
    err_file = log_dir / f"{datetime_str}.err"
    err_file.touch(exist_ok=True)

    # Create output data directories if not existing
    data_dir = root_dir / "data" / ROBOT_NAME[-3:]
    data_dir.mkdir(parents=True, exist_ok=True)
    data_subdirs = ["residuals", "contours", "node-dtbs", "cell-center-dtbs"]
    for directory in data_subdirs:
        dir_path = data_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print_log("info", f"{directory} path: {dir_path}", log_file)
    residuals_dir = data_dir / data_subdirs[0]
    contours_dir = data_dir / data_subdirs[1]
    node_dtbs_dir = data_dir / data_subdirs[2]
    cell_dtbs_dir = data_dir / data_subdirs[3]

    # Start the automatic process
    for config_id, config_name in enumerate(config_names):
        # Create the output parameters file if not existing.
        out_file = data_dir / f"out-{config_name}.csv"
        if not out_file.exists():
            with open(str(out_file), "w") as f:
                out_header = (
                    "config,pitch_angle,yaw_angle,ironcub-cd,ironcub-cl,ironcub-cs"
                )
                for surface in robot.surface_list:
                    report = surface[8:].replace("_", "-")
                    out_header = out_header + f",{report}-cd,{report}-cl,{report}-cs"
                f.writelines(out_header + "\n")
        else:
            with open(str(out_file), "w") as f:
                f.writelines("#### Restarting the process ####\n")
        # Get the output parameters
        out_list = get_output_param_list(out_file)

        # Define list of yaw angles (different for first config to restart a crushed process)
        yaw_angle_list = yaw_angle_start_list if config_id == 0 else yaw_angle_list

        # Launch Fluent
        time = datetime.now().strftime("%H:%M:%S")
        print_log("info", f"[{time}] Starting pyfluent session.", log_file)
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

        # Start the cycle on yaw angles
        for yaw_angle in yaw_angle_list:
            # Singular configuration check:
            # |yaw_angle| == 90 => wind direction not changing with pitch angle
            pitch_angle_list = (
                pitch_angle_list if (abs(abs(yaw_angle) - 90) > 1e-4) else [0.0]
            )
            # Start the cycle on pitch angles
            for pitch_angle in pitch_angle_list:

                try:
                    # Read the case file for the current joint configuration
                    cas_file = config_name + ".cas.h5"
                    cas_path = cas_dir / cas_file
                    solver.file.read_case(file_name=str(cas_path))

                    # Rotate the mesh according to pitch and yaw angles
                    solver.mesh.rotate(
                        angle=np.deg2rad(pitch_angle),
                        origin=[0, 0, 0],
                        axis_components=[-1, 0, 0],
                    )
                    solver.mesh.rotate(
                        angle=np.deg2rad(yaw_angle),
                        origin=[0, 0, 0],
                        axis_components=[0, 1, 0],
                    )

                    # Set Boundary Conditions
                    inlet = solver.setup.boundary_conditions.velocity_inlet["inlet"]
                    inlet.turbulence.turbulent_intensity = 0.001
                    solver.mesh.modify_zones.sep_face_zone_mark(
                        face_zone_name="inlet", register_name="region_in"
                    )
                    solver.mesh.modify_zones.zone_type(
                        zone_names=["inlet"], new_type="pressure-outlet"
                    )

                    # Initialize and solve the flow field
                    solver.solution.initialization.hybrid_initialize()
                    solver.solution.run_calculation.iterate(iter_count=ITER_NUM)

                    # Plot and save residuals (TODO: currently not working on srv and ws)
                    # solver.results.graphics.picture.use_window_resolution = True
                    # solver.results.graphics.picture.x_resolution = 1920
                    # solver.results.graphics.picture.y_resolution = 1440
                    # solver.results.graphics.picture.save_picture(
                    #     file_name = str( residuals_dir / f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}")
                    #     )

                    # Plot and save contours (TODO: currently not working on srv and ws)
                    # solver.results.graphics.contour["velocity-contour"] = {}
                    # solver.results.graphics.contour["velocity-contour"] = {
                    #     "field": "velocity-magnitude",
                    #     "surfaces_list": ["yz-plane"],
                    #     "node_values": True,
                    #     "range_option": {
                    #         "option": "auto-range-on",
                    #         "auto_range_on": {"global_range": False},
                    #     },
                    # }
                    # solver.results.graphics.contour.display(object_name="velocity-contour")
                    # solver.results.graphics.views.restore_view(view_name="right")
                    # solver.results.graphics.picture.save_picture(
                    #     file_name = str( contours_dir / f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}")
                    #     )

                    # Compute and write output parameters
                    out_val_list = solver.solution.report_definitions.compute(
                        report_defs=out_list
                    )
                    with open(str(out_file), "a") as f:
                        out_str = f"{config_name},{pitch_angle},{yaw_angle}"
                        for out_idx, _ in enumerate(out_list):
                            out_val = out_val_list[out_idx][out_list[out_idx]][0]
                            out_str = out_str + f",{out_val}"
                        f.writelines(out_str + "\n")

                    # Export surface data
                    cd_report = solver.solution.report_definitions.drag["ironcub-cd"]
                    surface_list = cd_report.zones.allowed_values()

                    exp_vars = [
                        "pressure",
                        "x-wall-shear",
                        "y-wall-shear",
                        "z-wall-shear",
                        "cell-id",
                        "x-face-area",
                        "y-face-area",
                        "z-face-area",
                    ]

                    # Export database files for each single surface
                    for rep_surf in robot.surface_list:
                        rep_surf_list = [rep_surf]
                        rep_surf_pref = rep_surf + ":"
                        for surface in surface_list:
                            if rep_surf_pref in surface:
                                rep_surf_list.extend([surface])
                        dtbs_file = f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-{rep_surf}.dtbs"
                        # Save cell data
                        dtbs_path = str(cell_dtbs_dir / dtbs_file)
                        solver.file.export.ascii(
                            file_name=dtbs_path,
                            surface_name_list=rep_surf_list,
                            delimiter="space",
                            cell_func_domain=exp_vars,
                            location="cell-center",
                        )
                        # Save node data
                        dtbs_path = str(node_dtbs_dir / dtbs_file)
                        solver.file.export.ascii(
                            file_name=dtbs_path,
                            surface_name_list=rep_surf_list,
                            delimiter="space",
                            cell_func_domain=exp_vars,
                            location="node",
                        )

                    # Export database files for all surfaces in the same file
                    rep_surf_list = []
                    for rep_surf in robot.surface_list:
                        rep_surf_list.append(rep_surf)
                        rep_surf_pref = rep_surf + ":"
                        for surface in surface_list:
                            if rep_surf_pref in surface:
                                rep_surf_list.append(surface)
                    dtbs_file = (
                        f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-robot.dtbs"
                    )
                    # Save cell data
                    dtbs_path = str(cell_dtbs_dir / dtbs_file)
                    solver.file.export.ascii(
                        file_name=dtbs_path,
                        surface_name_list=rep_surf_list,
                        delimiter="space",
                        cell_func_domain=exp_vars,
                        location="cell-center",
                    )
                    # Save node data
                    dtbs_path = str(node_dtbs_dir / dtbs_file)
                    solver.file.export.ascii(
                        file_name=dtbs_path,
                        surface_name_list=rep_surf_list,
                        delimiter="space",
                        cell_func_domain=exp_vars,
                        location="node",
                    )

                    # Print Iter End message
                    end_time = datetime.now().strftime("%H:%M:%S")
                    message = f"[{end_time}] {config_name}, alpha={pitch_angle}, beta={yaw_angle}: Success!"
                    print_log("info", message, log_file)

                except Exception as e:
                    message = f"[{end_time}] {config_name}, alpha={pitch_angle}, beta={yaw_angle}: Error!"
                    print_log("error", message, log_file)
                    with open(str(err_file), "a") as f:
                        f.writelines(message + "\n" + str(e) + "\n")

        # Close Fluent Solver Session
        solver.exit()
        time = datetime.now().strftime("%H:%M:%S")
        string = f"[{time}] {config_name} iterations completed!"
        print_log("success", string, log_file)

    # Close the process
    time = datetime.now().strftime("%H:%M:%S")
    string = f"[{time}] Automatic CFD process completed successfully!"
    print_log("success", string, log_file)


if __name__ == "__main__":
    main()
