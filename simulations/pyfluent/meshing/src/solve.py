"""
Author: Antonello Paolino
Date: 2025-03-28
"""

import ansys.fluent.core as pyfluent
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

    def read_mesh(self, config_name):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = Const.msh_dir / msh_file_name
        self.file.read_mesh(file_name=str(msh_file_path))
        self.solver.mesh.check()

    def modify_boundaries(self):
        self.solver.mesh.modify_zones.zone_type(
            zone_names=["outlet"], new_type="velocity-inlet"
        )
        self.solver.mesh.modify_zones.merge_zones(zone_names=["inlet", "outlet"])
        self.solver.solution.cell_registers["region_in"] = {}
        region_in = self.solver.solution.cell_registers["region_in"]
        region_in.type.option = "hexahedron"
        region_in.type.hexahedron.min_point = [-100, -100, -1]
        region_in.type.hexahedron.max_point = [100, 100, 100]

    def set_viscous_model(self):
        viscous = self.solver.setup.models.viscous
        viscous.model = Const.viscous_model
        viscous.k_omega_model = Const.viscous_model_type

    def set_boundary_conditions(self):
        inlet = self.solver.setup.boundary_conditions.velocity_inlet["inlet"]
        inlet.momentum.velocity_specification_method = "Magnitude and Direction"
        inlet.momentum.velocity = Const.inlet_velocity
        inlet.momentum.flow_direction = Const.inlet_velocity_dir
        inlet.turbulence.turbulent_specification = "Intensity and Viscosity Ratio"
        inlet.turbulence.turbulent_intensity = Const.inlet_turbulence_intensity
        inlet.turbulence.turbulent_viscosity_ratio_real = (
            Const.inlet_turbulence_viscosity_ratio
        )
        self.solver.setup.reference_values.velocity.set_state(
            inlet.momentum.velocity.value.get_state()
        )

    def set_methods(self):
        self.methods.p_v_coupling.flow_scheme.set_state("Coupled")
        self.methods.warped_face_gradient_correction.enable = True
        self.methods.warped_face_gradient_correction.mode = "memory-saving"
        self.methods.pseudo_time_method.formulation.coupled_solver = "off"
        for equation in self.solver.solution.monitor.residual.equations.keys():
            self.solver.solution.monitor.residual.equations[
                equation
            ].check_convergence = False

    def create_report_definitions(self, def_surface_list):
        coeff_names = ["-C_D", "-C_L", "-C_S"]
        force_vectors = [[0, 0, -1], [0, 1, 0], [-1, 0, 0]]
        # define the global reports for the ironcub force coefficients
        for coeff_name, force_vector in zip(coeff_names, force_vectors):
            self.solution.report_definitions.drag["ironcub" + coeff_name] = {}
            rd = self.solution.report_definitions.drag["ironcub" + coeff_name]
            self.surface_list = rd.zones.allowed_values()
            rd.zones = self.surface_list
            rd.force_vector = force_vector
            rd.average_over = Const.rd_average_over
        # define the local reports for the ironcub force coefficients
        for rep_surf in def_surface_list:
            rep_def_name = rep_surf[8:]
            rep_def_name = rep_def_name.replace("_", "-")
            rep_surf_list = [rep_surf]
            # check for duplicates of the main report surface
            rep_surf_pref = rep_surf + ":"
            for surface in self.surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            # define surface reports
            for coeff_name, force_vector in zip(coeff_names, force_vectors):
                rep_def_coeff_name = rep_def_name + coeff_name
                self.solution.report_definitions.drag[rep_def_coeff_name] = {}
                rd = self.solution.report_definitions.drag[rep_def_coeff_name]
                rd.zones = rep_surf_list
                rd.force_vector = force_vector
                rd.average_over = Const.rd_average_over

    def create_contour_plane(self):
        self.solver.results.surfaces.plane_surface.create("yz-plane")
        yz_plane = self.solver.results.surfaces.plane_surface["yz-plane"]
        yz_plane.method = "yz-plane"
        yz_plane.x = 0.0

    def initialize_solution(self):
        self.solution.initialization.hybrid_initialize()

    def write_dual_mesh(self, def_surface_list, config_name):
        for rep_surf in def_surface_list:
            rep_surf_list = [rep_surf]
            rep_surf_pref = rep_surf + ":"
            for surface in self.surface_list:
                if rep_surf_pref in surface:
                    rep_surf_list.extend([surface])
            dtbs_file_name = f"{config_name}-{rep_surf}.dlm"
            dtbs_file_path = str(Const.dlm_dir / dtbs_file_name)
            self.solver.file.export.ascii(
                file_name=dtbs_file_path,
                surface_name_list=rep_surf_list,
                delimiter="space",
                cell_func_domain=["x-face-area", "y-face-area", "z-face-area"],
                location="cell-center",
            )

    def write_case(self, config_name):
        cas_file_name = config_name + ".cas.h5"
        cas_file_path = Const.cas_dir / cas_file_name
        self.file.write(file_name=str(cas_file_path), file_type="case")

    def close(self):
        self.solver.exit()
