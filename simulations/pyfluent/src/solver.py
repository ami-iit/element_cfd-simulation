"""
Author: Antonello Paolino
Date: 2025-03-28
"""

import ansys.fluent.core as pyfluent
import os
import numpy as np
from datetime import datetime


def initialize_directories(root):
    cas_dir = root / "output" / "meshing" / "cas"
    out_dir = root / "output" / "solution"
    out_dir.mkdir(parents=True, exist_ok=True)
    residuals_dir = out_dir / "residuals"
    residuals_dir.mkdir(parents=True, exist_ok=True)
    contours_dir = out_dir / "contours"
    contours_dir.mkdir(parents=True, exist_ok=True)
    node_dtbs_dir = out_dir / "node-dtbs"
    node_dtbs_dir.mkdir(parents=True, exist_ok=True)
    cell_dtbs_dir = out_dir / "cell-dtbs"
    cell_dtbs_dir.mkdir(parents=True, exist_ok=True)
    aero_coefs_dir = out_dir / "aero-coefs"
    aero_coefs_dir.mkdir(parents=True, exist_ok=True)
    log_dir = out_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return (
        cas_dir,
        residuals_dir,
        contours_dir,
        node_dtbs_dir,
        cell_dtbs_dir,
        aero_coefs_dir,
        log_dir,
        out_dir,
    )


def initialize_log_files(log_dir):
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    log_file = log_dir / f"solution-{datetime_str}.log"
    log_file.touch(exist_ok=True)
    err_file = log_dir / f"solution-{datetime_str}.err"
    err_file.touch(exist_ok=True)
    return log_file, err_file


def get_joint_config_names(joint_config_file):
    with open(str(joint_config_file), "r") as f:
        config_file = f.readlines()
        config_names = []
        for config_name in config_file:
            temp = config_name.split(",")
            config_names.append(temp[0])
    return config_names


def get_angles(angles_file):
    with open(str(angles_file), "r") as f:
        file = f.readlines()
        angles = []
        for angle in file:
            temp = angle.strip().split(",")
            temp = [s for s in temp if s]
            angles.extend(temp)
    return angles


def get_surface_list(config):
    surface_list = []
    for elem in config["geometry"].keys():
        if "links" in elem:
            surface_list += config["geometry"][elem]
    return surface_list


def initialize_output_coefficients_file(config_name, options, aero_coefs_dir):
    surface_list = get_surface_list(options)
    # Create the output parameters file if not existing.
    out_file = aero_coefs_dir / f"coefs-{config_name}.csv"
    if not out_file.exists():
        with open(str(out_file), "w") as f:
            out_header = "config,pitch,yaw,ironcub-C_D,ironcub-C_L,ironcub-C_S"
            for surface in surface_list:
                report = surface.replace("_", "-")
                out_header = out_header + f",{report}-C_D,{report}-C_L,{report}-C_S"
            f.writelines(out_header + "\n")
    else:
        with open(str(out_file), "a") as f:
            f.writelines("#### Restarting the process ####\n")


class Solution:
    def __init__(self, options, log_directory, log_file, err_file):
        mpi_option = "-mpi=openmpi" if os.name == "posix" else ""
        self.log_dir = log_directory
        self.solver = pyfluent.launch_fluent(
            mode="solver",
            precision="double",
            product_version=options["general"]["fluent_version"],
            dimension=3,
            processor_count=options["general"]["core_num"],
            gpu=options["general"]["use_gpu"],
            ui_mode="no_gui_or_graphics",
            start_transcript=False,
            cwd=str(self.log_dir),
            additional_arguments=mpi_option,
        )
        self.file = self.solver.settings.file
        self.mesh = self.solver.settings.mesh
        self.setup = self.solver.settings.setup
        self.solution = self.solver.settings.solution
        self.methods = self.solution.methods
        self.surface_list = get_surface_list(options)
        self.options = options["solver"]
        self.log_file = log_file
        self.err_file = err_file

    def get_output_coefficients_list(self, config_name, aero_coefs_dir):
        self.out_coefs_file = aero_coefs_dir / f"coefs-{config_name}.csv"
        with open(str(self.out_coefs_file), "r") as out_csv:
            out_file = out_csv.readlines()
            out_coefs_list = out_file[0][:-1].split(",")
        self.out_coefs_list = out_coefs_list[3:]

    def read_mesh(self, config_name, msh_dir):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = msh_dir / msh_file_name
        self.file.read_mesh(file_name=str(msh_file_path))
        self.mesh.check()

    def load_case(self, config_name, cas_dir):
        cas_file_name = config_name + ".cas.h5"
        cas_file_path = cas_dir / cas_file_name
        self.file.read_case(file_name=str(cas_file_path))
        self.mesh.check()

    def rotate_mesh(self, pitch_angle, yaw_angle):
        # Rotate the mesh according to pitch and yaw angles
        self.mesh.rotate(
            angle=np.deg2rad(np.float64(pitch_angle)),
            origin=[0, 0, 0],
            axis_components=[-1, 0, 0],
        )
        self.mesh.rotate(
            angle=np.deg2rad(np.float64(yaw_angle)),
            origin=[0, 0, 0],
            axis_components=[0, 1, 0],
        )

    def modify_boundaries(self):
        self.mesh.modify_zones.zone_type(
            zone_names=["outlet"], new_type="velocity-inlet"
        )
        self.mesh.modify_zones.merge_zones(zone_names=["inlet", "outlet"])
        self.solution.cell_registers["region_in"] = {}
        region_in = self.solution.cell_registers["region_in"]
        region_in.type.option = "hexahedron"
        region_in.type.hexahedron.min_point = [-100, -100, -1]
        region_in.type.hexahedron.max_point = [100, 100, 100]

    def set_viscous_model(self):
        viscous = self.setup.models.viscous
        viscous.model = self.options["viscous_model"]
        viscous.k_omega_model = self.options["viscous_model_type"]

    def prepare_boundary_conditions(self):
        inlet = self.setup.boundary_conditions.velocity_inlet["inlet"]
        inlet.momentum.velocity_specification_method = "Magnitude and Direction"
        inlet.momentum.velocity_magnitude = self.options["inlet_velocity"]
        inlet.momentum.flow_direction = self.options["inlet_velocity_dir"]
        inlet.turbulence.turbulence_specification = "Intensity and Viscosity Ratio"
        inlet.turbulence.turbulent_intensity = self.options["in_turb_int"]
        inlet.turbulence.turbulent_viscosity_ratio = self.options["in_turb_visc_ratio"]
        self.setup.reference_values.velocity.set_state(
            inlet.momentum.velocity.value.get_state()
        )

    def set_boundary_conditions(self):
        inlet = self.setup.boundary_conditions.velocity_inlet["inlet"]
        inlet.turbulence.turbulent_intensity = self.options["in_turb_int"]
        inlet.turbulence.turbulent_viscosity_ratio = self.options["in_turb_visc_ratio"]
        self.mesh.modify_zones.sep_face_zone_mark(
            face_zone_name="inlet", register_name="region_in"
        )
        self.mesh.modify_zones.zone_type(
            zone_names=["inlet"], new_type="pressure-outlet"
        )

    def set_methods(self):
        self.methods.p_v_coupling.flow_scheme.set_state("Coupled")
        self.methods.warped_face_gradient_correction.enable = True
        self.methods.warped_face_gradient_correction.mode = "memory-saving"
        self.methods.pseudo_time_method.formulation.coupled_solver = "off"
        for equation in self.solution.monitor.residual.equations.keys():
            self.solution.monitor.residual.equations[equation].check_convergence = False

    def create_report_definitions(self):
        coeff_names = ["-C_D", "-C_L", "-C_S"]
        force_vectors = [[0, 0, -1], [0, 1, 0], [-1, 0, 0]]
        # define the global reports for the ironcub force coefficients
        for coeff_name, force_vector in zip(coeff_names, force_vectors):
            self.solution.report_definitions.drag["ironcub" + coeff_name] = {}
            rd = self.solution.report_definitions.drag["ironcub" + coeff_name]
            self.all_surface_list = rd.zones.allowed_values()
            rd.zones = self.all_surface_list
            rd.force_vector = force_vector
            rd.average_over = self.options["report_average_over"]
        # define the local reports for the ironcub force coefficients
        for rep_surf in self.surface_list:
            rep_def_name = rep_surf.replace("_", "-")
            rep_surf_list = [rep_surf]
            # check for duplicates of the main report surface
            rep_surf_pref = rep_surf + ":"
            for surface in self.all_surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            # define surface reports
            for coeff_name, force_vector in zip(coeff_names, force_vectors):
                rep_def_coeff_name = rep_def_name + coeff_name
                self.solution.report_definitions.drag[rep_def_coeff_name] = {}
                rd = self.solution.report_definitions.drag[rep_def_coeff_name]
                rd.zones = rep_surf_list
                rd.force_vector = force_vector
                rd.average_over = self.options["report_average_over"]

    def create_contour_plane(self):
        self.solver.settings.results.surfaces.plane_surface.create("yz-plane")
        yz_plane = self.solver.settings.results.surfaces.plane_surface["yz-plane"]
        yz_plane.method = "yz-plane"
        yz_plane.x = 0.0

    def initialize_solution(self):
        self.solution.initialization.hybrid_initialize()

    def run_simulation(self):
        self.solution.run_calculation.iterate(iter_count=self.options["iterations"])

    def export_surface_data(
        self, config_name, pitch_angle, yaw_angle, cell_dtbs_dir, node_dtbs_dir
    ):
        cd_report = self.solution.report_definitions.drag["ironcub-C_D"]
        self.all_surface_list = cd_report.zones.allowed_values()
        exp_vars = [
            "cell-id",
            "x-face-area",
            "y-face-area",
            "z-face-area",
        ]
        if self.options["export_pressure"]:
            exp_vars.append("pressure")
        if self.options["export_wall_shear_stress"]:
            exp_vars.extend(
                [
                    "x-wall-shear",
                    "y-wall-shear",
                    "z-wall-shear",
                ]
            )
        if self.options["export_velocity_gradients"]:
            exp_vars.extend(
                [
                    "viscosity-ratio",  # viscosity-turb / viscosity-lam
                    "dx-velocity-dx",
                    "dy-velocity-dx",
                    "dz-velocity-dx",
                    "dx-velocity-dy",
                    "dy-velocity-dy",
                    "dz-velocity-dy",
                    "dx-velocity-dz",
                    "dy-velocity-dz",
                    "dz-velocity-dz",
                ]
            )
        # Export database files for each single surface
        for rep_surf in self.surface_list:
            rep_surf_list = [rep_surf]
            rep_surf_pref = rep_surf + ":"
            for surface in self.all_surface_list:  # check redundancies
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            dtbs_file = (
                f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-{rep_surf}.dtbs"
            )
            # Save cell data
            dtbs_path = str(cell_dtbs_dir / dtbs_file)
            self.file.export.ascii(
                file_name=dtbs_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=exp_vars,
                location="cell-center",
            )
            # Save node data
            dtbs_path = str(node_dtbs_dir / dtbs_file)
            self.file.export.ascii(
                file_name=dtbs_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=exp_vars,
                location="node",
            )

        # Export database files for all surfaces in the same file
        rep_surf_list = []
        for rep_surf in self.surface_list:
            rep_surf_list.append(rep_surf)
            rep_surf_pref = rep_surf + ":"
            for surface in self.all_surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.append(surface)
        dtbs_file = f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-robot.dtbs"
        # Save cell data
        dtbs_path = str(cell_dtbs_dir / dtbs_file)
        self.file.export.ascii(
            file_name=dtbs_path,
            surface_name_list=rep_surf_list,
            delimiter="space",
            cell_func_domain=exp_vars,
            location="cell-center",
        )
        # Save node data
        dtbs_path = str(node_dtbs_dir / dtbs_file)
        self.file.export.ascii(
            file_name=dtbs_path,
            surface_name_list=rep_surf_list,
            delimiter="space",
            cell_func_domain=exp_vars,
            location="node",
        )

    def compute_output_coefs(self, config_name, pitch_angle, yaw_angle):
        out_val_list = self.solution.report_definitions.compute(
            report_defs=self.out_coefs_list
        )
        with open(str(self.out_coefs_file), "a") as f:
            out_str = f"{config_name},{pitch_angle},{yaw_angle}"
            for out_idx, out_name in enumerate(self.out_coefs_list):
                out_val = out_val_list[out_idx][out_name][0]
                out_str = out_str + f",{out_val}"
            f.writelines(out_str + "\n")

    def write_dual_mesh(self, config_name, dlm_dir):
        for rep_surf in self.surface_list:
            rep_surf_list = [rep_surf]
            rep_surf_pref = rep_surf + ":"
            for surface in self.all_surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            dtbs_file_name = f"{config_name}-{rep_surf}.dlm"
            dtbs_file_path = str(dlm_dir / dtbs_file_name)
            self.file.export.ascii(
                file_name=dtbs_file_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=["x-face-area", "y-face-area", "z-face-area"],
                location="cell-center",
            )

    def write_residuals(self, config_name, pitch_angle, yaw_angle, residuals_dir):
        res_file_name = (
            f"{config_name}-{int(pitch_angle)}-{int(yaw_angle)}-residuals.res"
        )
        res_file_path = residuals_dir / res_file_name
        self.solution.monitor.residual.write(filename=str(res_file_path))

    def write_case(self, config_name, cas_dir):
        cas_file_name = config_name + ".cas.h5"
        cas_file_path = cas_dir / cas_file_name
        self.file.write(file_name=str(cas_file_path), file_type="case")

    def close(self):
        self.solver.exit()
