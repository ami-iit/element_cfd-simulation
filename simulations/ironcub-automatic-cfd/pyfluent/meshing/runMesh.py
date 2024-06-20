"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This code uses the pyFluent packages to generate a mesh and set up 
                simulation parameters to perfom automatic CFD simulations starting 
                from a given iRonCub CAD model.

This code is based on the example provided at the following link: 
                
https://github.com/ansys/pyfluent/tree/v0.19.2/examples/00-fluent
"""

# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import ansys.fluent.core as pyfluent
from datetime import datetime

import pathlib
import os

from src.utils import colors, getJointConfigNames, cleanFilesExceptExtension

###############################################################################
# Set the name of the robot
# ~~~~~~~~~~~~~
# Set robot model: ironcub-mk1 | ironcub-mk3

robotName = "ironcub-mk3"

if robotName == "ironcub-mk1":
    import src.mk1 as robot
elif robotName == "ironcub-mk3":
    import src.mk3 as robot

###############################################################################
# Set the Fluent configuration parameters
# ~~~~~~~~~~~~~
# Set the parameters for the Fluent session

core_number = 12    # number of cores (only pre-post if use_gpu=True)
use_gpu = False     # use GPU native solver

# Set the MPI option for the WS
mpi_option = "-mpi=openmpi" if os.name == "posix" else ""

###############################################################################
# Define directory and file paths, load joint configuration names
# ~~~~~~~~~~~~~
# Define the paths for the directories and the files used in the process.

# Define dir paths
rootPath = pathlib.Path(__file__).parents[0]
parentPath = pathlib.Path(__file__).parents[1]
meshDirPath = rootPath / "mesh" / robotName[-3:] # mesh directory path
caseDirPath = rootPath / "case" / robotName[-3:] # Fluent case directory path
srcDirPath  = rootPath / "src"  # source directory path
logDirPath  = rootPath / "log"  # log directory path
geomDirPath = parentPath / "geom" / robotName[-3:] # geometry directory path

# Define file paths
jointConfigFilePath = srcDirPath / f"jointConfig-{robotName[-3:]}.csv"  # joint configuration file path

# Load the joint configuration names from the files.
jointConfigNames = getJointConfigNames(jointConfigFilePath)

###############################################################################
# Start the automatic process
# ~~~~~~~~~~~~~
# Start a cycle on all the provided joint configurations to generate the mesh
# and set up the simulation parameters for each of them.

for jointConfigName in jointConfigNames:

    # Define geometry file and path for current configuration
    geomFileName = geomDirPath / jointConfigName / "Geom.scdoc"

    try:
        ###############################################################################
        # Launch Fluent
        # ~~~~~~~~~~~~~
        # Launch Fluent as a service in meshing mode with double precision.

        timeFluentStart = datetime.now().strftime("%H:%M:%S")
        print(f"[{timeFluentStart}] Starting pyFluent session...")

        meshing = pyfluent.launch_fluent(
            mode="meshing",                     # "meshing", "pure-meshing" or "solver"
            precision="double",                 # single or double precision
            product_version="24.1.0",           # Fluent version
            version="3d",                       # 2d or 3d Fluent version
            processor_count=core_number,        # number of cores (only pre-post if use_gpu=True)
            gpu=use_gpu,                        # use GPU native solver
            start_transcript=False,             # start transcript file
            cwd=str(logDirPath),                # working directory
            additional_arguments=mpi_option,    # additional arguments (used for MPI option)
        )

        ###############################################################################
        # Watertight geometry meshing workflow
        # ------------------------------------
        # Initialize the watertight geometry meshing workflow.
        
        meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

        # Import CAD and set length units
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Import the CAD geometry and set the length units to meters.

        importGeometry = meshing.workflow.TaskObject["Import Geometry"]
        importGeometry.Arguments.set_state(
            {
                "FileName": str(geomFileName),
                "LengthUnit": "mm",
            }
        )
        importGeometry.Execute()

        ###############################################################################
        # Add local sizing
        # ~~~~~~~~~~~~~~~~
        # Add local sizing controls to the faceted geometry.

        addLocalSizing = meshing.workflow.TaskObject["Add Local Sizing"]
        addLocalSizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": "ironcub-sizing",
                "BOIFaceLabelList": robot.ironcubSurfacesList,
                "BOISize": 20,
            }
        )
        addLocalSizing.AddChildAndUpdate()
        addLocalSizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": "external-sizing",
                "BOIFaceLabelList": ["inlet", "outlet"],
                "BOISize": 2000,
            }
        )
        addLocalSizing.AddChildAndUpdate()

        ###############################################################################
        # Generate surface mesh
        # ~~~~~~~~~~~~~~~~~~~~~
        # Generate the surface mash.

        generateSurfaceMesh = meshing.workflow.TaskObject["Generate the Surface Mesh"]
        generateSurfaceMesh.Arguments.set_state(
            {
                "CFDSurfaceMeshControls": {
                    "MaxSize": 4000,
                    "MinSize": 5,
                    "SizeFunctions": robot.surfaceMeshSizeFunction,
                },
                "ExecuteShareTopology": "Yes",
            }
        )
        generateSurfaceMesh.Execute()

        ###############################################################################
        # Describe geometry
        # ~~~~~~~~~~~~~~~~~
        # Describe geometry and define the fluid region.

        describeGeometry = meshing.workflow.TaskObject["Describe Geometry"]
        describeGeometry.UpdateChildTasks(SetupTypeChanged=False)
        describeGeometry.Arguments.set_state(
            {"SetupType": "The geometry consists of both fluid and solid regions and/or voids"}
        )
        describeGeometry.UpdateChildTasks(SetupTypeChanged=True)
        describeGeometry.Execute()

        ###############################################################################
        # Apply Share Topology
        # ~~~~~~~~~~~~~~~~~
        # Describe geometry and define the fluid region.

        applyShareTopology = meshing.workflow.TaskObject["Apply Share Topology"]
        applyShareTopology.Arguments.set_state(
            {
                "GapDistance": 2.5,
                "ShareTopologyPreferences": {"Operation": "Join-Intersect"},
            }
        )
        applyShareTopology.Execute()

        ###############################################################################
        # Update boundaries and regions
        # ~~~~~~~~~~~~~~~~~
        # Update the boundaries and regions.

        meshing.workflow.TaskObject["Update Boundaries"].Execute()
        meshing.workflow.TaskObject["Update Regions"].Execute()

        ###############################################################################
        # Add boundary layers
        # ~~~~~~~~~~~~~~~~~~~
        # Add boundary layers, which consist of setting properties for the
        # boundary layer mesh.

        addBoundaryLayer = meshing.workflow.TaskObject["Add Boundary Layers"]
        addBoundaryLayer.Arguments.set_state(
            {
                "LocalPrismPreferences": {
                    "Continuous": "Stair Step",
                    "ShowLocalPrismPreferences": False,
                },
                "NumberOfLayers": 5,
            }
        )
        addBoundaryLayer.AddChildAndUpdate()

        ###############################################################################
        # Generate and improve volume mesh
        # ~~~~~~~~~~~~~~~~~~~~
        # Generate the poly-hexcore volume mesh and improve quality.

        generateVolumeMesh = meshing.workflow.TaskObject["Generate the Volume Mesh"]
        generateVolumeMesh.Arguments.set_state(
            {
                "MeshSolidRegions": False,
                "PrismPreferences": {"ShowPrismPreferences": False},
                "VolumeFill": "poly-hexcore",
                "VolumeFillControls": {
                    "HexMaxCellLength": 2560,
                    "HexMinCellLength": 40,
                    "PeelLayers": 2,
                },
                "VolumeMeshPreferences": {"ShowVolumeMeshPreferences": False},
            }
        )
        generateVolumeMesh.Execute()
        generateVolumeMesh.InsertNextTask(CommandName="ImproveVolumeMesh")
        improveVolumeMesh = meshing.workflow.TaskObject["Improve Volume Mesh"]
        improveVolumeMesh.Arguments.set_state(
            {
                "CellQualityLimit": 0.15,
                "QualityMethod": "Orthogonal",
                "VMImprovePreferences": {
                    "ShowVMImprovePreferences": True,
                    "VIQualityIterations": 5,
                    "VIQualityMinAngle": 0,
                    "VIgnoreFeature": "yes",
                },
            }
        )
        improveVolumeMesh.Execute()

        ###############################################################################
        # Check mesh, save mesh file and exit meshing mode
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Check the mesh in meshing mode.

        meshing.tui.mesh.check_mesh()
        meshFileName = jointConfigName + ".msh.h5"
        meshFilePath = meshDirPath / meshFileName
        meshing.tui.file.write_mesh(str(meshFilePath))
        meshing.exit()

        ###############################################################################
        # Re-launch Fluent in solver mode
        # ~~~~~~~~~~~~~
        # Launch Fluent as a service in solver mode with double precision.

        timeFluentStart = datetime.now().strftime("%H:%M:%S")
        print(f"[{timeFluentStart}] Starting pyFluent session...")

        solver = pyfluent.launch_fluent(
            mode="solver",                     # "meshing", "pure-meshing" or "solver"
            precision="double",                 # single or double precision
            product_version="24.1.0",           # Fluent version
            version="3d",                       # 2d or 3d Fluent version
            processor_count=core_number,        # number of cores (only pre-post if use_gpu=True)
            gpu=use_gpu,                        # use GPU native solver
            start_transcript=False,             # start transcript file
            cwd=str(logDirPath),                # working directory
            additional_arguments=mpi_option,    # additional arguments (used for MPI option)
        )

        ###############################################################################
        # Load and check the mesh
        # ~~~~~~~~~~~~~
        # Load and check the mesh file for the current joint configuration.
        
        solver.file.read_mesh(file_name=str(meshFilePath))
        solver.mesh.check()

        ###############################################################################
        # Modify zones and regions
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Merging the inlet and outlet zones and creating a region to split the inlet

        solver.mesh.modify_zones.zone_type(zone_names = ["outlet"], new_type = "velocity-inlet")
        solver.mesh.modify_zones.merge_zones(zone_names = ["inlet", "outlet"])

        solver.solution.cell_registers["region_in"] = {}
        region_in = solver.solution.cell_registers["region_in"]
        region_in.type.option = "hexahedron"
        region_in.type.hexahedron.min_point = [-100, -100, -1]
        region_in.type.hexahedron.max_point = [100, 100, 100]

        ###############################################################################
        # Simulation Setup
        # ~~~~~~~~~~~~
        # Set up the simulation parameters.

        # Set the viscous model to k-w sst
        viscous = solver.setup.models.viscous
        viscous.model = "k-omega"
        viscous.k_omega_model = "sst"

        # Boundary Conditions
        inlet = solver.setup.boundary_conditions.velocity_inlet["inlet"]
        inlet.momentum.velocity_specification_method = "Magnitude and Direction"
        inlet.momentum.velocity = 17.0
        inlet.momentum.flow_direction = [0.0, 0.0, -1.0]
        inlet.turbulence.turbulent_specification = "Intensity and Viscosity Ratio"
        inlet.turbulence.turbulent_intensity = 0.001
        inlet.turbulence.turbulent_viscosity_ratio_real = 0.01

        # Reference values (for non-dimensionalization)
        solver.setup.reference_values.velocity.set_state(inlet.momentum.velocity.value.get_state())

        # Solver methods
        solver.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")
        solver.solution.methods.warped_face_gradient_correction.enable = True
        solver.solution.methods.warped_face_gradient_correction.mode = "memory-saving"
        solver.solution.methods.pseudo_time_method.formulation.coupled_solver = "off"
        for equation in solver.solution.monitor.residual.equations.keys():
            solver.solution.monitor.residual.equations[equation].check_convergence = False

        ###############################################################################
        # Report Definitions
        # ~~~~~~~~~~~~~~~~~~~~
        # Define the report defintions for automatic updates of the results.

        # initialize ironcub cd, cl, cs reports
        solver.solution.report_definitions.drag["ironcub-cd"] = {}
        solver.solution.report_definitions.drag["ironcub-cl"] = {}
        solver.solution.report_definitions.drag["ironcub-cs"] = {}
        # define ironcub cd, cl, cs reports
        cd = solver.solution.report_definitions.drag["ironcub-cd"]
        cl = solver.solution.report_definitions.drag["ironcub-cl"]
        cs = solver.solution.report_definitions.drag["ironcub-cs"]
        # get the complete list of surfaces from cd report
        surfaceList = cd.zones.allowed_values()
        # set ironcub-cd report
        cd.zones = surfaceList
        cd.force_vector = [0, 0, -1]
        cd.average_over = 100
        # set ironcub-cl report
        cl.zones = surfaceList
        cl.force_vector = [0, 1, 0]
        cl.average_over = 100
        # set ironcub-cs report
        cs.zones = surfaceList
        cs.force_vector = [-1, 0, 0]
        cs.average_over = 100

        # define the reports for the ironcub surfaces
        for reportSurface in robot.ironcubSurfacesList:
            if reportSurface in robot.surfaceSkipList:
                continue
            else:
                reportDefName = reportSurface[8:]
                reportDefName = reportDefName.replace("_", "-")
                reportSurfaceList = [reportSurface]
                # check for duplicates of the main report surface
                reportSurfacePrefix = reportSurface+":"
                for surface in surfaceList:
                    if reportSurfacePrefix in surface:  
                        reportSurfaceList.extend([surface])
                # Add skip surfaces if the main report surface is a merge surface
                if reportSurface in robot.surfaceMergeList:
                    addSurfaceList = [robot.surfaceSkipList[index] for index, value in enumerate(robot.surfaceMergeList) if value == reportSurface]
                    reportSurfaceList.extend(addSurfaceList)
                    # check for duplicates of the skip surfaces
                    for addSurface in addSurfaceList:
                        addSurfacePrefix = addSurface+":"
                        for surface in surfaceList:
                            if addSurfacePrefix in surface:  
                                reportSurfaceList.extend([surface])
                # define surface cd report
                solver.solution.report_definitions.drag[reportDefName + "-cd"] = {}
                cd = solver.solution.report_definitions.drag[reportDefName + "-cd"]
                cd.zones = reportSurfaceList
                cd.force_vector = [0, 0, -1]
                cd.average_over = 100
                # define surface cl report
                solver.solution.report_definitions.drag[reportDefName + "-cl"] = {}
                cl = solver.solution.report_definitions.drag[reportDefName + "-cl"]
                cl.zones = reportSurfaceList
                cl.force_vector = [0, 1, 0]
                cl.average_over = 100
                # define surface cs report
                solver.solution.report_definitions.drag[reportDefName + "-cs"] = {}
                cs = solver.solution.report_definitions.drag[reportDefName + "-cs"]
                cs.zones = reportSurfaceList
                cs.force_vector = [-1, 0, 0]
                cs.average_over = 100


        ###############################################################################
        # Contour Plane Defintions
        # ~~~~~~~~~~~~~~~~~~~~
        # Define the YZ plane on which to plot the contours.

        solver.results.surfaces.plane_surface.create("yz-plane")
        yz_plane = solver.results.surfaces.plane_surface["yz-plane"]
        yz_plane.method = "yz-plane"
        yz_plane.x = 0.0

        ###############################################################################
        # Initialize flow field and save case file
        # ~~~~~~~~~~~~~~~~~~~~~
        # Initialize the flow field using hybrid initialization.

        solver.solution.initialization.hybrid_initialize()

        caseFileName = jointConfigName + ".cas.h5"
        caseFilePath = (caseDirPath / caseFileName)
        solver.file.write(file_name=str(caseFilePath), file_type="case")

        ###############################################################################
        # Close Fluent and clean up debug files
        # ~~~~~~~~~~~~
        # Close Fluent, print the end message and cleanup the debug files.

        solver.exit()

        timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
        print(
            colors.GREEN,
            f"[{timeJointConfigEnd}] {jointConfigName} mesh generated!",
            colors.RESET,
        )
        cleanFilesExceptExtension(meshDirPath, ".h5")
        cleanFilesExceptExtension(logDirPath, [".log", ".trn", ".bat"])


    except Exception as exceptionMessage:
        ###############################################################################
        # Manage Fluent errors
        # ~~~~~~~~~~~~
        # Close Fluent, print an error message, cleanup the debug files and skip the configuration.

        meshing.exit()

        timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
        print(
            colors.RED,
            f"[{timeJointConfigEnd}] {jointConfigName} mesh failed with the following error: \n",
            exceptionMessage,
            colors.RESET,
        )
        cleanFilesExceptExtension(meshDirPath, ".h5")
        cleanFilesExceptExtension(logDirPath, [".log", ".trn", ".bat"])

        pass

###############################################################################
# Close the process
# ~~~~~~~~~~~~
# Print the process end message

timeProcessEnd = datetime.now().strftime("%H:%M:%S")
print(
    colors.GREEN,
    f"[{timeProcessEnd}] Automatic meshing process completed!",
    colors.RESET,
)
