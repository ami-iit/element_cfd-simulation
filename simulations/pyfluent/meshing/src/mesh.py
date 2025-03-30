"""
Author: Antonello Paolino
Date: 2025-03-28
"""

import ansys.fluent.core as pyfluent
import os

from src import log
from src.constants import Const


class Mesh:
    def __init__(self):
        mpi_option = "-mpi=openmpi" if os.name == "posix" else ""
        self.meshing = pyfluent.launch_fluent(
            mode="meshing",
            precision="double",
            product_version="24.1.0",
            dimension=3,
            processor_count=Const.core_num,
            gpu=Const.use_gpu,
            start_transcript=False,
            cwd=str(Const.log_dir),
            additional_arguments=mpi_option,
        )
        self.wf = self.meshing.workflow
        self.tui = self.meshing.tui

    def initialize_workflow(self):
        self.wf.InitializeWorkflow(WorkflowType=Const.workflow)

    def import_geometry(self, config_name):
        geom_file = "Geom.scdoc.pmdb" if os.name == "posix" else "Geom.scdoc"
        geom_path = Const.geom_dir / config_name / geom_file
        if not geom_path.exists():
            log.print_error(f"{geom_file} not found!")
        import_geom = self.wf.TaskObject["Import Geometry"]
        import_geom.Arguments.set_state(
            {
                "FileName": str(geom_path),
                "LengthUnit": Const.ig_length_unit,
            }
        )
        import_geom.Execute()

    def add_robot_local_sizings(self, surface_list):
        local_sizing = self.wf.TaskObject["Add Local Sizing"]
        local_sizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": Const.ls_robot_sizing_name,
                "BOIFaceLabelList": surface_list,
                "BOISize": Const.ls_robot_sizing,
                "BOIExecution": "Face Size",
            }
        )
        local_sizing.AddChildAndUpdate()

    def add_boundary_local_sizings(self):
        local_sizing = self.wf.TaskObject["Add Local Sizing"]
        local_sizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": Const.ls_boundary_sizing_name,
                "BOIFaceLabelList": ["inlet", "outlet"],
                "BOISize": Const.ls_boundary_sizing,
                "BOIExecution": "Face Size",
            }
        )
        local_sizing.AddChildAndUpdate()

    def generate_surface_mesh(self):
        surface_mesh = self.wf.TaskObject["Generate the Surface Mesh"]
        surface_mesh.Arguments.set_state(
            {
                "CFDSurfaceMeshControls": {
                    "MaxSize": Const.gsm_max_size,
                    "MinSize": Const.gsm_min_size,
                    "SizeFunctions": Const.gsm_size_function,
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
                "GapDistance": Const.st_gap_distance,
                "ShareTopologyPreferences": {"Operation": Const.st_operation},
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
                "NumberOfLayers": Const.bl_layers,
            }
        )
        boundary_layer.AddChildAndUpdate()

    def generate_volume_mesh(self):
        volume_mesh = self.wf.TaskObject["Generate the Volume Mesh"]
        volume_mesh.Arguments.set_state(
            {
                "MeshSolidRegions": False,
                "PrismPreferences": {"ShowPrismPreferences": False},
                "VolumeFill": Const.gvm_mesh_type,
                "VolumeFillControls": {
                    "HexMaxCellLength": Const.gvm_max_hex_cell_length,
                    "HexMinCellLength": Const.gvm_min_hex_cell_length,
                    "PeelLayers": Const.gvm_peel_layers,
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
                "CellQualityLimit": Const.ivm_quality_limit,
                "QualityMethod": Const.ivm_quality_method,
                "VMImprovePreferences": {
                    "ShowVMImprovePreferences": True,
                    "VIQualityIterations": Const.ivm_quality_iter,
                    "VIQualityMinAngle": Const.ivm_quality_min_angle,
                    "VIgnoreFeature": "yes",
                },
            }
        )
        improve_volume_mesh.Execute()

    def check_mesh(self):
        self.tui.mesh.check_mesh()

    def write_mesh(self, config_name):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = Const.msh_dir / msh_file_name
        self.tui.file.write_mesh(str(msh_file_path))

    def read_mesh(self, config_name):
        msh_file_name = config_name + ".msh.h5"
        msh_file_path = Const.msh_dir / msh_file_name
        self.tui.file.read_mesh(str(msh_file_path))

    def export_boundary_mesh(self, surface_list, config_name):
        for surface in surface_list:
            filename = Const.msh_dir / f"{config_name}-{surface}.msh"
            self.tui.file.write_boundaries(str(filename), surface)

    def close(self):
        self.meshing.exit()
