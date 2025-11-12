"""
Author: Antonello Paolino
Date: 2025-03-28
"""

import ansys.fluent.core as pyfluent
import os
from datetime import datetime

# src modules
from src import log


def initialize_directories(root):
    geom_dir = root / "output" / "geometry" / "geometries"
    out_dir = root / "output" / "meshing"
    msh_dir = out_dir / "msh"
    msh_dir.mkdir(parents=True, exist_ok=True)
    dlm_dir = out_dir / "dlm"
    dlm_dir.mkdir(parents=True, exist_ok=True)
    cas_dir = out_dir / "cas"
    cas_dir.mkdir(parents=True, exist_ok=True)
    log_dir = out_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    return geom_dir, msh_dir, dlm_dir, cas_dir, log_dir


def initialize_log_files(log_dir):
    datetime_str = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    log_file = log_dir / f"mesh-{datetime_str}.log"
    log_file.touch(exist_ok=True)
    err_file = log_dir / f"mesh-{datetime_str}.err"
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


def get_surface_list(config):
    surface_list = []
    for elem in config["geometry"].keys():
        if "links" in elem:
            surface_list += config["geometry"][elem]
    return surface_list


class Mesh:
    def __init__(self, options, log_dir, log_file, err_file):
        mpi_option = "-mpi=openmpi" if os.name == "posix" else ""
        self.meshing = pyfluent.launch_fluent(
            mode="meshing",
            precision="double",
            product_version=options["general"]["fluent_version"],
            dimension=3,
            processor_count=options["general"]["core_num"],
            gpu=options["general"]["use_gpu"],
            start_transcript=False,
            cwd=str(log_dir),
            additional_arguments=mpi_option,
        )
        self.wf = self.meshing.workflow
        self.tui = self.meshing.tui
        self.surface_list = get_surface_list(options)
        self.options = options["meshing"]
        self.log_file = log_file
        self.err_file = err_file

    def initialize_workflow(self):
        self.wf.InitializeWorkflow(WorkflowType=self.options["workflow"])

    def import_geometry(self, config_name, geometry_dir):
        geom_path = geometry_dir / f"{config_name}" / "geometry.pmdb"
        if not geom_path.exists():
            log.print_err(f"{geom_path} not found!", self.log_file, self.err_file)
        import_geom = self.wf.TaskObject["Import Geometry"]
        import_geom.Arguments.set_state(
            {
                "FileName": str(geom_path),
                "LengthUnit": self.options["import_geometry_length_unit"],
            }
        )
        import_geom.Execute()

    def add_robot_local_sizings(self):
        local_sizing = self.wf.TaskObject["Add Local Sizing"]
        local_sizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": self.options["robot_face_sizing_name"],
                "BOIFaceLabelList": self.surface_list,
                "BOISize": self.options["robot_face_sizing"],
                "BOIExecution": "Face Size",
            }
        )
        local_sizing.AddChildAndUpdate()

    def add_boundary_local_sizings(self):
        local_sizing = self.wf.TaskObject["Add Local Sizing"]
        local_sizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": self.options["boundary_face_sizing_name"],
                "BOIFaceLabelList": ["inlet", "outlet"],
                "BOISize": self.options["boundary_face_sizing"],
                "BOIExecution": "Face Size",
            }
        )
        local_sizing.AddChildAndUpdate()

    def generate_surface_mesh(self):
        surface_mesh = self.wf.TaskObject["Generate the Surface Mesh"]
        surface_mesh.Arguments.set_state(
            {
                "CFDSurfaceMeshControls": {
                    "MaxSize": self.options["surface_mesh_max_size"],
                    "MinSize": self.options["surface_mesh_min_size"],
                    "SizeFunctions": self.options["surface_mesh_size_function"],
                },
                "ExecuteShareTopology": "Yes",
            }
        )
        surface_mesh.Execute()

    def describe_geometry(self):
        describe_geom = self.wf.TaskObject["Describe Geometry"]
        describe_geom.UpdateChildTasks(SetupTypeChanged=False)
        describe_geom.Arguments.set_state(
            {
                "SetupType": "The geometry consists of both fluid and solid regions and/or voids"
            }
        )
        describe_geom.UpdateChildTasks(SetupTypeChanged=True)
        describe_geom.Execute()

    def apply_share_topology(self):
        share_topology = self.wf.TaskObject["Apply Share Topology"]
        share_topology.Arguments.set_state(
            {
                "GapDistance": self.options["share_topology_gap_distance"],
                "ShareTopologyPreferences": {
                    "Operation": self.options["share_topology_operation"]
                },
            }
        )
        share_topology.Execute()

    def update_boundaries_and_regions(self):
        self.wf.TaskObject["Update Boundaries"].Execute()
        self.wf.TaskObject["Update Regions"].Execute()

    def add_boundary_layer(self):
        boundary_layer = self.wf.TaskObject["Add Boundary Layers"]
        boundary_layer.Arguments.set_state(
            {
                "LocalPrismPreferences": {
                    "Continuous": "Stair Step",
                    "ShowLocalPrismPreferences": False,
                },
                "NumberOfLayers": self.options["boundary_layer_layers"],
            }
        )
        boundary_layer.AddChildAndUpdate()

    def generate_volume_mesh(self):
        volume_mesh = self.wf.TaskObject["Generate the Volume Mesh"]
        volume_mesh.Arguments.set_state(
            {
                "MeshSolidRegions": False,
                "PrismPreferences": {"ShowPrismPreferences": False},
                "VolumeFill": self.options["volume_mesh_type"],
                "VolumeFillControls": {
                    "HexMaxCellLength": self.options["volume_mesh_max_hex_cell_length"],
                    "HexMinCellLength": self.options["volume_mesh_min_hex_cell_length"],
                    "PeelLayers": self.options["volume_mesh_peel_layers"],
                },
                "VolumeMeshPreferences": {"ShowVolumeMeshPreferences": False},
            }
        )
        volume_mesh.Execute()

    def improve_volume_mesh(self):
        volume_mesh = self.wf.TaskObject["Generate the Volume Mesh"]
        volume_mesh.InsertNextTask(CommandName="ImproveVolumeMesh")
        improve_volume_mesh = self.wf.TaskObject["Improve Volume Mesh"]
        improve_volume_mesh.Arguments.set_state(
            {
                "CellQualityLimit": self.options["improve_mesh_quality_limit"],
                "QualityMethod": self.options["improve_mesh_quality_method"],
                "VMImprovePreferences": {
                    "ShowVMImprovePreferences": True,
                    "VIQualityIterations": self.options["improve_mesh_quality_iter"],
                    "VIQualityMinAngle": self.options["improve_mesh_quality_min_angle"],
                    "VIgnoreFeature": "yes",
                },
            }
        )
        improve_volume_mesh.Execute()

    def check_mesh(self):
        self.tui.mesh.check_mesh()

    def write_mesh(self, config_name, msh_dir):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = msh_dir / msh_file_name
        self.tui.file.write_mesh(str(msh_file_path))

    def read_mesh(self, config_name, msh_dir):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = msh_dir / msh_file_name
        self.tui.file.read_mesh(str(msh_file_path))

    def export_boundary_mesh(self, config_name, msh_dir):
        for surface in self.surface_list:
            filename = msh_dir / f"{config_name}-{surface}.msh"
            self.tui.file.write_boundaries(str(filename), surface)

    def close(self):
        self.meshing.exit()
