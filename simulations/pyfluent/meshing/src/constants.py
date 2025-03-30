"""
Author: Antonello Paolino
Date: 2025-02-12
Description: Implementing a singleton class for storing the constant values.
"""


def singleton(cls):
    return cls()


@singleton
class Const:
    def __init__(self):
        # general settings
        self.config_path = None
        self.robot_name = None
        # directories
        self.config_dir = None
        self.geom_dir = None
        self.out_dir = None
        self.msh_dir = None
        self.dlm_dir = None
        self.cas_dir = None
        self.log_dir = None
        self.log_file = None
        self.err_file = None
        # fluent settings
        self.core_num = 64
        self.use_gpu = False
        # meshing settings
        self.workflow = "Watertight Geometry"
        self.ig_length_unit = "mm"
        self.ls_robot_sizing_name = "ironcub-sizing"
        self.ls_robot_sizing = 20
        self.ls_boundary_sizing_name = "boundary-sizing"
        self.ls_boundary_sizing = 2000
        self.gsm_max_size = 4000
        self.gsm_min_size = 5
        self.gsm_size_function = "Curvature & Proximity"
        self.st_gap_distance = 2.5
        self.st_operation = "Join-Intersect"
        self.bl_layers = 5
        self.gvm_mesh_type = "poly-hexcore"
        self.gvm_max_hex_cell_length = 2560
        self.gvm_min_hex_cell_length = 40
        self.gvm_peel_layers = 2
        self.ivm_quality_limit = 0.15
        self.ivm_quality_method = "Orthogonal"
        self.ivm_quality_iter = 5
        self.ivm_quality_min_angle = 0
        # solver settings
        self.viscous_model = "k-omega"
        self.viscous_model_type = "sst"
        self.inlet_velocity = 17.0
        self.inlet_velocity_dir = [0.0, 0.0, -1.0]
        self.inlet_turbulence_intensity = 0.001
        self.inlet_turbulence_viscosity_ratio = 0.01
        self.rd_average_over = 100

    def get_default_values(self):
        default_values = {}
        for key, value in self.__dict__.items():
            default_values[key] = value
        return default_values

    def set_val_from_options(self, options):
        for key, value in options.items():
            setattr(Const, key.lower(), self.convert_value(value))

    def convert_value(self, value):
        if value.lower() in ("true", "false", "yes", "no"):
            return value.lower() == "true" or value.lower() == "yes"
        elif value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value  # Return as string if conversion fails
