"""
Author: Antonello Paolino
Date: 2025-03-28
"""

import ansys.fluent.core as pyfluent
import numpy as np
import os

from src import log
from src.constants import Const


class Solver:
    def __init__(self):
        mpi_option = "-mpi=openmpi" if os.name == "posix" else ""
        self.solver = pyfluent.launch_fluent(
            mode="solver",
            precision="double",
            product_version="24.1.0",
            dimension=3,
            processor_count=Const.core_num,
            gpu=Const.use_gpu,
            start_transcript=False,
            cwd=str(Const.log_dir),
            additional_arguments=mpi_option,
        )
        self.file = self.solver.file
        self.solution = self.solver.solution
        self.methods = self.solution.methods

    def get_output_coefficients_list(self, config_name):
        self.out_coefs_file = Const.aero_coefs_dir / f"coefs-{config_name}.csv"
        with open(str(self.out_coefs_file), "r") as out_csv:
            out_file = out_csv.readlines()
            out_coefs_list = out_file[0][:-1].split(",")
        self.out_coefs_list = out_coefs_list[3:]

    def load_case(self, config_name):
        cas_file_name = config_name + ".cas.h5"
        cas_file_path = Const.cas_dir / cas_file_name
        self.file.read_case(file_name=str(cas_file_path))
        self.solver.mesh.check()

    def rotate_mesh(self, pitch_angle, yaw_angle):
        # Rotate the mesh according to pitch and yaw angles
        self.solver.mesh.rotate(
            angle=np.deg2rad(np.float64(pitch_angle)),
            origin=[0, 0, 0],
            axis_components=[-1, 0, 0],
        )
        self.solver.mesh.rotate(
            angle=np.deg2rad(np.float64(yaw_angle)),
            origin=[0, 0, 0],
            axis_components=[0, 1, 0],
        )

    def set_boundary_conditions(self):
        inlet = self.solver.setup.boundary_conditions.velocity_inlet["inlet"]
        inlet.turbulence.turbulent_intensity = Const.inlet_turbulence_intensity
        self.solver.mesh.modify_zones.sep_face_zone_mark(
            face_zone_name="inlet", register_name="region_in"
        )
        self.solver.mesh.modify_zones.zone_type(
            zone_names=["inlet"], new_type="pressure-outlet"
        )

    def initialize_solution(self):
        self.solver.solution.initialization.hybrid_initialize()

    def run_calculation(self):
        self.solver.solution.run_calculation.iterate(iter_count=Const.iterations)

    def plot_and_save_residuals(self, config_name, pitch_angle, yaw_angle):
        self.solver.results.graphics.picture.use_window_resolution = True
        self.solver.results.graphics.picture.x_resolution = 1920
        self.solver.results.graphics.picture.y_resolution = 1440
        self.solver.results.graphics.picture.save_picture(
            file_name=str(
                Const.residuals_dir
                / f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}"
            )
        )

    def plot_and_save_vel_contour(self, config_name, pitch_angle, yaw_angle):
        self.solver.results.graphics.contour["velocity-contour"] = {}
        self.solver.results.graphics.contour["velocity-contour"] = {
            "field": "velocity-magnitude",
            "surfaces_list": ["yz-plane"],
            "node_values": True,
            "range_option": {
                "option": "auto-range-on",
                "auto_range_on": {"global_range": False},
            },
        }
        self.solver.results.graphics.contour.display(object_name="velocity-contour")
        self.solver.results.graphics.views.restore_view(view_name="right")
        self.solver.results.graphics.picture.save_picture(
            file_name=str(
                Const.contours_dir
                / f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}"
            )
        )

    def compute_output_coefs(self, config_name, pitch_angle, yaw_angle):
        out_val_list = self.solver.solution.report_definitions.compute(
            report_defs=self.out_coefs_list
        )
        with open(str(self.out_coefs_file), "a") as f:
            out_str = f"{config_name},{pitch_angle},{yaw_angle}"
            for out_idx, out_name in enumerate(self.out_coefs_list):
                out_val = out_val_list[out_idx][out_name][0]
                out_str = out_str + f",{out_val}"
            f.writelines(out_str + "\n")

    def export_surface_data(
        self, config_name, pitch_angle, yaw_angle, def_surface_list
    ):
        cd_report = self.solver.solution.report_definitions.drag["ironcub-cd"]
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
        for rep_surf in def_surface_list:
            rep_surf_list = [rep_surf]
            rep_surf_pref = rep_surf + ":"
            for surface in surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            dtbs_file = (
                f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-{rep_surf}.dtbs"
            )
            # Save cell data
            dtbs_path = str(Const.cell_dtbs_dir / dtbs_file)
            self.solver.file.export.ascii(
                file_name=dtbs_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=exp_vars,
                location="cell-center",
            )
            # Save node data
            dtbs_path = str(Const.node_dtbs_dir / dtbs_file)
            self.solver.file.export.ascii(
                file_name=dtbs_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=exp_vars,
                location="node",
            )

        # Export database files for all surfaces in the same file
        rep_surf_list = []
        for rep_surf in def_surface_list:
            rep_surf_list.append(rep_surf)
            rep_surf_pref = rep_surf + ":"
            for surface in surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.append(surface)
        dtbs_file = f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-robot.dtbs"
        # Save cell data
        dtbs_path = str(Const.cell_dtbs_dir / dtbs_file)
        self.solver.file.export.ascii(
            file_name=dtbs_path,
            surface_name_list=rep_surf_list,
            delimiter="space",
            cell_func_domain=exp_vars,
            location="cell-center",
        )
        # Save node data
        dtbs_path = str(Const.node_dtbs_dir / dtbs_file)
        self.solver.file.export.ascii(
            file_name=dtbs_path,
            surface_name_list=rep_surf_list,
            delimiter="space",
            cell_func_domain=exp_vars,
            location="node",
        )

    def close(self):
        self.solver.exit()
