'''
Author: Antonello Paolino
Date: 2024-01-29
Description: This code uses the pyFluent packages to generate a mesh and run a simulations starting from a given iRonCub CAD model.
'''

# import packages
import ansys.fluent.core as pyfluent
from ansys.fluent.visualization import set_config
from ansys.fluent.visualization.matplotlib import Plots
from ansys.fluent.visualization.pyvista import Graphics
from datetime import datetime

import numpy as np 
import pathlib
import os

from src.utils import getOutputParameterList, getJointConfigNames, cleanFilesExceptExtension

######################### SIMULATION SETTINGS ##################################
core_number         = 16        # number of cores to use (only pre-post mode if gpu is True)
use_gpu             = True      # use GPU native solver
iteration_number    = 1000      # number of iterations to run in the solver

################################# MPI OPTION ####################################
# this fixes the MPI error on Linux setting MPI to openmpi (needed for the ws)
if os.name == "posix":
    mpi_option = "-mpi=openmpi"
else:
    mpi_option = ""

################################# PATHS DEFINITION ############################## 
# Define root folder path
rootPath = pathlib.Path(__file__).parents[0]

# Define case, data, source and log directory paths
geomDirPath = rootPath / "geom" # geometry directory path
meshDirPath = rootPath / "mesh" # mesh directory path
caseDirPath = rootPath / "case" # Fluent case directory path
dataDirPath = rootPath / "data" # data directory path
srcDirPath  = rootPath / "src"  # source directory path
logPath     = rootPath / "log"  # log directory path

# Define file names
jointConfigFileName    = "jointConfig.csv"
outputParamFileName    = "outputParameters.csv"

# Define file paths
jointConfigFilePath    = srcDirPath / jointConfigFileName       # joint configuration file path
outputParamFilePath    = dataDirPath / outputParamFileName      # output parameters file path

######################### PROCESS PARAMETERS LOADING ############################
# Load output parameters list from file
outputParameterList = getOutputParameterList(outputParamFilePath)
    
# Load robot joint config names
jointConfigNames = getJointConfigNames(jointConfigFilePath)

############################## Start the automatic process ########################
# Cycle on the configurations
for jointConfigName in jointConfigNames:
    
    # Define geometry file and path for current configuration
    geomFileName = geomDirPath / jointConfigName / 'Geom.scdoc'

    ####################### Launch Fluent Meshing session via pyFluent #######################
    timeFluentStart = datetime.now().strftime("%H:%M:%S")
    print(f"[{timeFluentStart}] Starting pyFluent session...")
    meshing = pyfluent.launch_fluent(
        mode="meshing",                     # "meshing", "pure-meshing" or "solver"
        precision="double",                 # single or double precision
        version="3d",                       # 2d or 3d Fluent version
        processor_count=core_number,        # number of processors (only pre-post mode if gpu is True)
        gpu=use_gpu,                        # use GPU native solver
        start_transcript=False,             # start transcript file
        cwd=str(logPath),                   # working directory
        show_gui=False,                     # show GUI or not
        additional_arguments=mpi_option)    # additional arguments (used for MPI option)
    
    ####################### Watertight Workflow #######################
    # Initialize workflow
    meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    
    # Import geometry
    geo_import = meshing.workflow.TaskObject["Import Geometry"]
    geo_import.Arguments = {
        "FileName": str(geomFileName),
        "LengthUnit": "m",
        }
    geo_import.Execute()
    
    # Add ironcub sizing
    add_local_sizing = meshing.workflow.TaskObject["Add Local Sizing"]
    add_local_sizing.Arguments = {
        "AddChild": "yes",
        "BOIControlName": "ironcub-sizing",
        "BOIFaceLabelList": [
            'ironcub_head', 'ironcub_left_back_turbine', 'ironcub_right_back_turbine', 
            'ironcub_left_arm', 'ironcub_left_arm_pitch', 'ironcub_left_arm_roll', 'ironcub_left_turbine',
            'ironcub_left_leg_lower', 'ironcub_left_leg_pitch', 'ironcub_left_leg_roll', 'ironcub_left_leg_upper',  
            'ironcub_right_arm', 'ironcub_right_arm_pitch', 'ironcub_right_arm_roll', 'ironcub_right_turbine',
            'ironcub_right_leg_lower', 'ironcub_right_leg_pitch', 'ironcub_right_leg_roll', 'ironcub_right_leg_upper',  
            'ironcub_root_link', 'ironcub_torso', 'ironcub_torso_pitch', 'ironcub_torso_roll'],
        'BOISize': 0.02,
        }
    add_local_sizing.AddChildToTask()
    add_local_sizing.Execute()
    
    # Add external sizing
    add_local_sizing = meshing.workflow.TaskObject["Add Local Sizing"]
    add_local_sizing.Arguments = {
        "AddChild": "yes",
        "BOIControlName": "external-sizing",
        "BOIFaceLabelList": ['inlet','outlet'],
        'BOISize': 2.00,
        }
    add_local_sizing.AddChildToTask()
    add_local_sizing.Execute()
    
    # Generate the Surface Mesh
    surface_mesh_gen = meshing.workflow.TaskObject["Generate the Surface Mesh"]
    surface_mesh_gen.Arguments = {
        'CFDSurfaceMeshControls': {
            'MaxSize': 4,
            'MinSize': 0.005,
            },
        'ExecuteShareTopology': 'Yes',
        }
    surface_mesh_gen.Execute()
    
    # Insert surface mesh improve task
    surface_mesh_gen.InsertNextTask(CommandName='ImproveSurfaceMesh')
    
    # Improve surface mesh
    improve_surface_mesh = meshing.workflow.TaskObject['Improve Surface Mesh']
    improve_surface_mesh.Arguments = {
        'FaceQualityLimit': 0.7,
        'MeshObject': '',
        'SMImprovePreferences': {
            'SIQualityCollapseLimit': 0.855,
            'SIQualityIterations': 5,
            'SIQualityMaxAngle': 160,
            'SIRemoveStep': 'no',
            'SIStepQualityLimit': 0,
            'SIStepWidth': 0,
            'ShowSMImprovePreferences': False,
            },
        'SQMinSize': 0.005,
        }
    improve_surface_mesh.Execute()
    
    # Describe Geometry
    describe_geom = meshing.workflow.TaskObject["Describe Geometry"]
    describe_geom.UpdateChildTasks(SetupTypeChanged=False)
    describe_geom.Arguments = {
        'SetupType': 'The geometry consists of both fluid and solid regions and/or voids',
        }
    describe_geom.UpdateChildTasks(SetupTypeChanged=True)
    describe_geom.Execute()

    # Apply Share Topology
    apply_share_topology = meshing.workflow.TaskObject["Apply Share Topology"]
    apply_share_topology.Arguments = {
        'GapDistance': 0.0025,
        'ShareTopologyPreferences': {
            'Operation': 'Join-Intersect',
            },
        }
    apply_share_topology.Execute()
    
    # Update boundaries
    update_boundaries = meshing.workflow.TaskObject['Update Boundaries']
    update_boundaries.Arguments = {
        'BoundaryLabelList': ['outlet', 'fluid-outlet', 'inlet', 'fluid-inlet'],
        'BoundaryLabelTypeList': ['pressure-outlet', 'pressure-outlet', 'velocity-inlet', 'velocity-inlet'],
        }
    update_boundaries.Execute()
    
    # Update regions
    update_regions = meshing.workflow.TaskObject['Update Regions']
    update_regions.Arguments = {
        'NumberOfFlowVolumes': 1,
        'RetainDeadRegionName': 'no',
        }
    update_regions.Execute()
    
    # Update regions
    meshing.workflow.TaskObject["Update Regions"].Execute()
    
    # Add boundary layer
    add_boundary_layer = meshing.workflow.TaskObject["Add Boundary Layers"]
    add_boundary_layer.Arguments= {
        'LocalPrismPreferences': {
            'Continuous': 'Stair Step',
            'ShowLocalPrismPreferences': False,
            },
        'NumberOfLayers': 5,
        }
    add_boundary_layer.AddChildAndUpdate()
    
    # Generate volume mesh
    generate_volume_mesh = meshing.workflow.TaskObject["Generate the Volume Mesh"]
    generate_volume_mesh.Arguments = {
        'MeshSolidRegions': False,
        'PrismPreferences': {
            'ShowPrismPreferences': False,
            },
        'VolumeFill': 'poly-hexcore',
        'VolumeFillControls': {
            'HexMaxCellLength': 2.56,
            'HexMinCellLength': 0.04,
            'PeelLayers': 2,
            },
        'VolumeMeshPreferences': {
            'ShowVolumeMeshPreferences': False,
            },
        }   
    generate_volume_mesh.Execute()
    
    # Insert volume mesh improve task
    generate_volume_mesh.InsertNextTask(CommandName='ImproveVolumeMesh')
    
    # Improve volume mesh
    improve_volume_mesh = meshing.workflow.TaskObject["Improve Volume Mesh"]
    improve_volume_mesh.Arguments = {
        'CellQualityLimit': 0.15,
        'QualityMethod': 'Orthogonal',
        'VMImprovePreferences': {
            'ShowVMImprovePreferences': True,
            'VIQualityIterations': 5,
            'VIQualityMinAngle': 0,
            'VIgnoreFeature': 'yes',
            },
        }
    improve_volume_mesh.Execute()
    
    # Check mesh
    meshing.tui.mesh.check_mesh()
    
    # Save mesh (to be removed when the solver will be added)
    meshFileName = jointConfigName + ".msh.h5"
    meshFilePath = meshDirPath / meshFileName
    meshing.tui.file.write_mesh(str(meshFilePath))
    
    # Close the meshing process
    # meshing.exit()
    
    ###########################################################
    ## Switching to solver process to setup the case file    
    # solver = pyfluent.launch_fluent(
    #     mode="solver",                      # "meshing", "pure-meshing" or "solver"
    #     precision="double",                 # single or double precision
    #     version="3d",                       # 2d or 3d Fluent version
    #     processor_count=core_number,        # number of processors (only pre-post mode if gpu is True)
    #     gpu=use_gpu,                        # use GPU native solver
    #     start_transcript=False,             # start transcript file
    #     cwd=str(logPath),                   # working directory
    #     show_gui=False,                     # show GUI or not
    #     additional_arguments=mpi_option)    # additional arguments (used for MPI option)
    
    # Read the generated mesh
    # solver.file.read_mesh(file_name=str(meshFilePath))
    
    # # Switch to solver mode
    solver = meshing.switch_to_solver()
    
    # Check again the mesh
    solver.mesh.check()
    
    # Merge inlet and outlet zones
    solver.tui.mesh.modify_zones.zone_type("outlet", "velocity-inlet")
    solver.tui.mesh.modify_zones.merge_zones("inlet", "outlet")
    
    # Create region_in to split later the inlet/outlet boundaries
    solver.tui.solve.cell_registers.add('region_in', 'type', 'hexahedron', 'min-point', -100, -100, -1, 'max-point', 100, 100, 100)
    
    
    # Define model: set the k-w SST turbulence model
    viscous = solver.setup.models.viscous
    viscous.model = "k-omega"
    viscous.k_omega_model = "sst"
    
    # Define BC: inlet
    boundary_conditions = solver.setup.boundary_conditions
    
    inlet = boundary_conditions.velocity_inlet["inlet"]
    inlet.velocity_spec.set_state("Magnitude and Direction")
    inlet.vmag = 17.0
    inlet.flow_direction = [0.0, 0.0, -1.0]
    inlet.turb_intensity = 0.1
    inlet.turb_viscosity_ratio = 0.01
    
    # Reference values
    solver.setup.reference_values.compute.from_zone_name.set_state('inlet')
    
    # Methods
    solver.solution.methods.p_v_coupling.flow_scheme.set_state('Coupled')
    solver.solution.methods.warped_face_gradient_correction.enable(enable=True, gradient_correction_mode='memory-saving-mode')
    
    ### Report definition generation
    solver.solution.report_definitions.force["test"] = {}
    surfacesList = solver.solution.report_definitions.force["test"].thread_names.allowed_values()
    
    surfacesSkipList = []
    surfacesMergeList = []
    
    for surfaceName in surfacesList:
        
        # define cd report
        solver.solution.report_definitions.drag[surfaceName+"-cd"] = {}
        cd = solver.solution.report_definitions.drag[surfaceName+"-cd"]
        cd.thread_names.set_state(surfaceName)
        cd.force_vector.set_state([0, 0, -1])
        cd.average_over.set_state(100)
        
        # define cl report
        solver.solution.report_definitions.drag[surfaceName+"-cl"] = {}
        cl = solver.solution.report_definitions.drag[surfaceName+"-cl"]
        cl.thread_names.set_state(surfaceName)
        cl.force_vector.set_state([0, 1, 0])
        cl.average_over.set_state(100)
        
        # define cs report
        solver.solution.report_definitions.drag[surfaceName+"-cs"] = {}
        cs = solver.solution.report_definitions.drag[surfaceName+"-cs"]
        cs.thread_names.set_state(surfaceName)
        cs.force_vector.set_state([-1, 0, 0])
        cs.average_over.set_state(100)
    
    # Create surface for contour plot
    solver.tui.surface.plane_surface('yz_plane yz-plane 0')         # Create the YZ plane
    
    # Hybrid Initialization
    solver.solution.initialization.hybrid_initialize()
    
    # Write case file
    caseFileName = jointConfigName + ".cas.h5"      # Fluent jointConfig case file name
    caseFilePath = caseDirPath / caseFileName       # Fluent jointConfig case file full path
    solver.file.write(file_name=str(caseFilePath), file_type="case")
    
    ###########################################################
    solver.exit()
    timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
    print(f"[{timeJointConfigEnd}] {jointConfigName} mesh generated!")
    
# Cleanup mesh directory
cleanFilesExceptExtension(meshDirPath, '.h5')

# End of the process message
timeProcessEnd = datetime.now().strftime("%H:%M:%S")
print(f"[{timeProcessEnd}] Automatic meshing process completed!")