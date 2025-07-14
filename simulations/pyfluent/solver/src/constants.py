"""
Author: Antonello Paolino
Date: 2025-05-07
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
        self.cas_dir = None
        self.out_dir = None
        self.residuals_dir = None
        self.contours_dir = None
        self.node_dtbs_dir = None
        self.cell_dtbs_dir = None
        self.aero_coefs_dir = None
        self.log_dir = None
        self.log_file = None
        self.err_file = None
        # fluent settings
        self.fluent_version = "24.1.0"
        self.core_num = 64
        self.use_gpu = False
        self.iterations = 1000
        # solver settings
        self.inlet_turbulence_intensity = 0.001
        # export variables
        self.export_pressure = True
        self.export_wall_shear_stress = True
        self.export_velocity_gradients = True

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
