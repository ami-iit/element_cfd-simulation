import sys
import configparser
import tabulate
from pathlib import Path
from datetime import datetime

from src.constants import Const


def read_config_file(argv):
    # Read configuration file
    print("Reading config file")
    if len(argv) < 2:
        print("\n\033[31mNo .cfg file provided in input.\nKilling execution \033[0m")
        sys.exit()
    Const.config_path = str(argv[1])
    # Create a temporary section header
    config_content = "[DEFAULT]\n"
    if not Path(Const.config_path).is_file():
        print(f"\nConfiguration file {Const.config_path} does not exist.\n")
        sys.exit()
    with open(Const.config_path, "r") as file:
        config_content += file.read()
    # Read options
    config = configparser.ConfigParser(comment_prefixes=("%",))
    config.read_string(config_content)
    # Retrieve options from the 'DEFAULT' section as dictionary
    options = dict(config.items("DEFAULT"))
    return options


def print_options(options, default_values):
    print("Configuration options:")
    headers = ["Option Name", "Option Value", "Origin"]
    # Sort data alphabetically by the option name
    all_values = {**default_values, **options}
    data = sorted(
        [
            (key.upper(), value, check_if_default(key, options, default_values))
            for key, value in all_values.items()
        ],
        key=lambda x: x[0],
    )
    print(tabulate.tabulate(data, headers=headers, tablefmt="grid"))


def check_if_default(key, options, default_values):
    # Check if a key is user-defined or default assigned.
    if key in options:
        return "User-defined"
    elif key in default_values and not key in options:
        return "Default"


def initialize_directories(root, parent):
    Const.config_dir = root / "config"
    Const.geom_dir = parent / "geom" / Const.robot_name
    Const.out_dir = root / "out" / Const.robot_name
    Const.out_dir.mkdir(parents=True, exist_ok=True)
    Const.msh_dir = Const.out_dir / "msh"
    Const.msh_dir.mkdir(parents=True, exist_ok=True)
    Const.dlm_dir = Const.out_dir / "dlm"
    Const.dlm_dir.mkdir(parents=True, exist_ok=True)
    Const.cas_dir = Const.out_dir / "cas"
    Const.cas_dir.mkdir(parents=True, exist_ok=True)
    Const.log_dir = Const.out_dir / "log"
    Const.log_dir.mkdir(parents=True, exist_ok=True)


def initialize_log_files():
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    Const.log_file = Const.log_dir / f"{datetime_str}.log"
    Const.log_file.touch(exist_ok=True)
    Const.err_file = Const.log_dir / f"{datetime_str}.err"
    Const.err_file.touch(exist_ok=True)


def get_joint_config_names():
    file = Const.config_dir / f"joint-config-{Const.robot_name}.csv"
    with open(str(file), "r") as f:
        config_file = f.readlines()
        config_names = []
        for config_name in config_file:
            temp = config_name.split(",")
            config_names.append(temp[0])
    return config_names


def get_surface_list():
    file = Const.config_dir / f"surface-list-{Const.robot_name}.csv"
    with open(str(file), "r") as f:
        surface_file = f.readlines()
        surface_list = []
        for surface in surface_file:
            temp = surface.strip().split(",")
            temp = [s for s in temp if s]
            surface_list.extend(temp)
    return surface_list
