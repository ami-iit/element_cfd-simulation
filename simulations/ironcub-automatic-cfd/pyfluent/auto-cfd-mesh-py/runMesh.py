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
from ansys.fluent.visualization import set_config
from ansys.fluent.visualization.matplotlib import Plots
from ansys.fluent.visualization.pyvista import Graphics
from datetime import datetime

import numpy as np
import pathlib
import os

from src.utils import colors, getOutputParameterList, getJointConfigNames, cleanFilesExceptExtension

###############################################################################
# Set the Fluent configuration parameters
# ~~~~~~~~~~~~~
# Set the parameters for the Fluent session

core_number = 48    # number of cores (only pre-post if use_gpu=True)
use_gpu = False     # use GPU native solver

# Set the MPI option for the WS
mpi_option = "-mpi=openmpi" if os.name == "posix" else ""

###############################################################################
# Define directory and file paths
# ~~~~~~~~~~~~~
# Define the paths for the directories and the files used in the process.

# Define dir paths

rootPath = pathlib.Path(__file__).parents[0]

geomDirPath = rootPath / "geom" # geometry directory path
meshDirPath = rootPath / "mesh" # mesh directory path
caseDirPath = rootPath / "case" # Fluent case directory path
dataDirPath = rootPath / "data" # data directory path
srcDirPath  = rootPath / "src"  # source directory path
logDirPath  = rootPath / "log"  # log directory path

# Define file paths

jointConfigFilePath = srcDirPath / "jointConfig.csv"  # joint configuration file path
outputParamFilePath = dataDirPath / "outputParameters.csv"  # output parameters file path

###############################################################################
# Load parameters from files
# ~~~~~~~~~~~~~
# Load the output parameters and the joint configuration names from the files.

outputParameterList = getOutputParameterList(outputParamFilePath)
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
            version="3d",                       # 2d or 3d Fluent version
            processor_count=core_number,        # number of cores (only pre-post if use_gpu=True)
            gpu=use_gpu,                        # use GPU native solver
            start_transcript=False,             # start transcript file
            cwd=str(logDirPath),                # working directory
            show_gui=False,                     # show GUI or not
            additional_arguments=mpi_option,    # additional arguments (used for MPI option)
        )

        ###############################################################################
        # Initialize workflow
        # ~~~~~~~~~~~~~~~~~~~
        # Initialize the watertight geometry meshing workflow.

        meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

        ###############################################################################
        # Watertight geometry meshing workflow
        # ------------------------------------
        # The watertight meshing workflow guides you through the several tasks that
        # follow.
        #
        # Import CAD and set length units
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Import the CAD geometry and set the length units to meters.

        importGeometry = meshing.workflow.TaskObject["Import Geometry"]
        importGeometry.Arguments.set_state(
            {
                "FileName": str(geomFileName),
                "LengthUnit": "m",
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
                "BOIFaceLabelList": [
                    "ironcub_head",
                    "ironcub_left_back_turbine",
                    "ironcub_right_back_turbine",
                    "ironcub_left_arm",
                    "ironcub_left_arm_pitch",
                    "ironcub_left_arm_roll",
                    "ironcub_left_turbine",
                    "ironcub_left_leg_lower",
                    "ironcub_left_leg_pitch",
                    "ironcub_left_leg_roll",
                    "ironcub_left_leg_upper",
                    "ironcub_right_arm",
                    "ironcub_right_arm_pitch",
                    "ironcub_right_arm_roll",
                    "ironcub_right_turbine",
                    "ironcub_right_leg_lower",
                    "ironcub_right_leg_pitch",
                    "ironcub_right_leg_roll",
                    "ironcub_right_leg_upper",
                    "ironcub_root_link",
                    "ironcub_torso",
                    "ironcub_torso_pitch",
                    "ironcub_torso_roll",
                ],
                "BOISize": 0.02,
            }
        )

        addLocalSizing.AddChildAndUpdate()

        addLocalSizing.Arguments.set_state(
            {
                "AddChild": "yes",
                "BOIControlName": "external-sizing",
                "BOIFaceLabelList": ["inlet", "outlet"],
                "BOISize": 2.00,
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
                    "MaxSize": 4,
                    "MinSize": 0.005,
                    # "SizeFunctions": "Curvature",
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
                "GapDistance": 0.0025,
                "ShareTopologyPreferences": {"Operation": "Join-Intersect"},
            }
        )

        applyShareTopology.Execute()


        ###############################################################################
        # Update boundaries
        # ~~~~~~~~~~~~~~~~~
        # Update the boundaries.

        meshing.workflow.TaskObject["Update Boundaries"].Execute()

        # update_boundaries = meshing.workflow.TaskObject['Update Boundaries']
        # update_boundaries.Arguments = {
        #     "BoundaryLabelList": ["outlet", "fluid-outlet", "inlet", "fluid-inlet"],
        #     "BoundaryLabelTypeList": ["pressure-outlet", "pressure-outlet", "velocity-inlet", "velocity-inlet"],
        #     }
        # update_boundaries.Execute()


        ###############################################################################
        # Update regions
        # ~~~~~~~~~~~~~~
        # Update the regions.

        meshing.workflow.TaskObject["Update Regions"].Execute()

        # update_regions = meshing.workflow.TaskObject["Update Regions"]
        # update_regions.Arguments = {
        #     "NumberOfFlowVolumes": 1,
        #     "RetainDeadRegionName": "no",
        #     }
        # update_regions.Execute()


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
        # Generate volume mesh
        # ~~~~~~~~~~~~~~~~~~~~
        # Generate the volume mesh, which consists of setting properties for the
        # volume mesh.

        generateVolumeMesh = meshing.workflow.TaskObject["Generate the Volume Mesh"]
        generateVolumeMesh.Arguments.set_state(
            {
                "MeshSolidRegions": False,
                "PrismPreferences": {"ShowPrismPreferences": False},
                "VolumeFill": "poly-hexcore",
                "VolumeFillControls": {
                    "HexMaxCellLength": 2.56,
                    "HexMinCellLength": 0.04,
                    "PeelLayers": 2,
                },
                "VolumeMeshPreferences": {"ShowVolumeMeshPreferences": False},
            }
        )

        generateVolumeMesh.Execute()

        # Insert volume mesh improve task
        generateVolumeMesh.InsertNextTask(CommandName="ImproveVolumeMesh")


        ###############################################################################
        # Improve volume mesh
        # ~~~~~~~~~~~~~~~~~~~~
        # Improve the quality of the volume mesh.

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
        # Check mesh in meshing mode
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Check the mesh in meshing mode.

        meshing.tui.mesh.check_mesh()


        ###############################################################################
        # Save mesh file
        # ~~~~~~~~~~~~~~
        # Save the mesh file.

        meshFileName = jointConfigName + ".msh.h5"
        meshFilePath = meshDirPath / meshFileName
        meshing.tui.file.write_mesh(str(meshFilePath))


        ###############################################################################
        # Switch to solution mode
        # ~~~~~~~~~~~~~~~~~~~~~~~
        # Switch to solution mode. Now that a high-quality mesh has been generated
        # using Fluent in meshing mode, you can switch to solver mode to complete the
        # setup of the simulation.

        solver = meshing.switch_to_solver()


        ###############################################################################
        # Check mesh in solver mode
        # ~~~~~~~~~~~~~~~~~~~~~~~~~
        # Check the mesh in solver mode. The mesh check lists the minimum and maximum
        # x, y, and z values from the mesh in the default SI units of meters. It also
        # reports a number of other mesh features that are checked. Any errors in the
        # mesh are reported.

        solver.mesh.check()


        ###############################################################################
        # Modify zones and regions
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Merging the inlet and outlet zones and creating a region to split the inlet

        solver.tui.mesh.modify_zones.zone_type("outlet", "velocity-inlet")
        solver.tui.mesh.modify_zones.merge_zones("inlet", "outlet")
        
        solver.tui.solve.cell_registers.add(
            'region_in', 'type', 'hexahedron', 'min-point', -100, -100, -1, 'max-point', 100, 100, 100
        )


        ###############################################################################
        # Define model
        # ~~~~~~~~~~~~
        # Set the k-w sst turbulence model.

        # model : k-omega
        # k-omega model : sst

        viscous = solver.setup.models.viscous

        viscous.model = "k-omega"
        viscous.k_omega_model = "sst"


        ###############################################################################
        # Boundary Conditions
        # ~~~~~~~~~~~~~~~~~~~
        # Set the boundary conditions for ``inlet``.

        # velocity magnitude = 17.0 [m/s]
        # velocity direction = [0.0, 0.0, 1.0]
        # turbulent intensity = 0.1 [%]
        # turbulent viscosity ratio = 0.01

        inlet = solver.setup.boundary_conditions.velocity_inlet["inlet"]

        inlet.velocity_spec.set_state("Magnitude and Direction")
        inlet.vmag = 17.0
        inlet.flow_direction = [0.0, 0.0, -1.0]
        inlet.turb_intensity = 0.1
        inlet.turb_viscosity_ratio = 0.01


        ###############################################################################
        # Reference values
        # ~~~~~~~~~~~~~~~~~~~~
        # Set the reference values to compute the aerodynamic coefficients.

        # reference velocity magnitude: inlet velocity magnitude

        solver.setup.reference_values.velocity.set_state(inlet.vmag.value())


        ###############################################################################
        # Methods
        # ~~~~~~~~~~~~~~~~~~~~
        # Set the solver computing methods.

        # Solver: Pressure-based Coupled
        # Warped Face Gradient Correction: ON

        solver.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")

        solver.solution.methods.warped_face_gradient_correction.enable(
            enable=True, gradient_correction_mode="memory-saving-mode"
        )

        # TODO change when upgrading to Fluent 24.1
        solver.tui.solve.monitors.residual.check_convergence(
            "no", "no", "no", "no", "no", "no"
        )


        ###############################################################################
        # Global Report Definitions
        # ~~~~~~~~~~~~~~~~~~~~
        # Define the global report defintions for automatic updates of the results.

        # initialize ironcub cd, cl, cs reports
        solver.solution.report_definitions.drag["ironcub-cd"] = {}
        solver.solution.report_definitions.drag["ironcub-cl"] = {}
        solver.solution.report_definitions.drag["ironcub-cs"] = {}

        # define ironcub cd, cl, cs reports
        cd = solver.solution.report_definitions.drag["ironcub-cd"]
        cl = solver.solution.report_definitions.drag["ironcub-cl"]
        cs = solver.solution.report_definitions.drag["ironcub-cs"]

        # get the complete list of surfaces from cd report
        surfaceList = cd.thread_names.allowed_values()

        # set cd report
        cd.thread_names.set_state(surfaceList)
        cd.force_vector.set_state([0, 0, -1])
        cd.average_over.set_state(100)

        # set cl report
        cl.thread_names.set_state(surfaceList)
        cl.force_vector.set_state([0, 1, 0])
        cl.average_over.set_state(100)

        # set cs report
        cs.thread_names.set_state(surfaceList)
        cs.force_vector.set_state([-1, 0, 0])
        cs.average_over.set_state(100)


        ###############################################################################
        # Local Report Definitions
        # ~~~~~~~~~~~~~~~~~~~~
        # Define the local report defintions for automatic updates of the results.

        # Define the surfaces skiplist (enclosed in the reports of the mergelist)

        surfaceSkipList = [
            "ironcub_left_arm_pitch",
            "ironcub_left_arm_roll",
            "ironcub_right_arm_pitch",
            "ironcub_right_arm_roll",
            "ironcub_left_leg_pitch",
            "ironcub_left_leg_roll",
            "ironcub_right_leg_pitch",
            "ironcub_right_leg_roll",
            "ironcub_torso_pitch",
            "ironcub_torso_roll",
        ]

        surfaceMergeList = [
            "ironcub_left_arm",
            "ironcub_left_arm",
            "ironcub_right_arm",
            "ironcub_right_arm",
            "ironcub_root_link",
            "ironcub_left_leg_upper",
            "ironcub_root_link",
            "ironcub_right_leg_upper",
            "ironcub_torso",
        ]

        # define the reports for the surfaces
        for surfaceName in surfaceList:

            if surfaceName in surfaceSkipList:

                continue

            else:

                reportSurfNames = [surfaceName]
                reportDefName = surfaceName[8:]
                reportDefName = reportDefName.replace("_", "-")

                if surfaceName in surfaceMergeList:     # add the skip surfaces to the report surface list
                    surfaceNamesAdd = [surfaceSkipList[index] for index, value in enumerate(surfaceMergeList) if value == surfaceName]
                    reportSurfNames.extend(surfaceNamesAdd)

                # define surface cd, cl, cs reports

                solver.solution.report_definitions.drag[reportDefName + "-cd"] = {}
                cd = solver.solution.report_definitions.drag[reportDefName + "-cd"]
                cd.thread_names.set_state(reportSurfNames)
                cd.force_vector.set_state([0, 0, -1])
                cd.average_over.set_state(100)

                solver.solution.report_definitions.drag[reportDefName + "-cl"] = {}
                cl = solver.solution.report_definitions.drag[reportDefName + "-cl"]
                cl.thread_names.set_state(reportSurfNames)
                cl.force_vector.set_state([0, 1, 0])
                cl.average_over.set_state(100)

                solver.solution.report_definitions.drag[reportDefName + "-cs"] = {}
                cs = solver.solution.report_definitions.drag[reportDefName + "-cs"]
                cs.thread_names.set_state(reportSurfNames)
                cs.force_vector.set_state([-1, 0, 0])
                cs.average_over.set_state(100)


        ###############################################################################
        # Contour Plane Defintions
        # ~~~~~~~~~~~~~~~~~~~~
        # Define the YZ plane on which to plot the contours.

        solver.tui.surface.plane_surface("yz_plane yz-plane 0")  # Create the YZ plane


        ###############################################################################
        # Initialize flow field
        # ~~~~~~~~~~~~~~~~~~~~~
        # Initialize the flow field using hybrid initialization.

        solver.solution.initialization.hybrid_initialize()


        ###############################################################################
        # Save case file
        # ~~~~~~~~~~~~~~
        # Save the case file.

        caseFileName = jointConfigName + ".cas.h5"  # Fluent jointConfig case file name
        caseFilePath = (caseDirPath / caseFileName) # Fluent jointConfig case file full path

        solver.file.write(file_name=str(caseFilePath), file_type="case")


        ###############################################################################
        # Close Fluent
        # ~~~~~~~~~~~~
        # Close Fluent and print the end message.

        solver.exit()

        timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
        print(
            colors.GREEN
            + f"[{timeJointConfigEnd}] {jointConfigName} mesh generated!"
            + colors.RESET,
        )


    except Exception as exceptionMessage:

        ###############################################################################
        # Manage Fluent errors
        # ~~~~~~~~~~~~
        # Close Fluent, print an error message and skip the configuration.

        meshing.exit()

        timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
        print(
            colors.RED
            + f"[{timeJointConfigEnd}] {jointConfigName} mesh failed with the following error: \n",
            exceptionMessage,
            colors.RESET,
        )

        pass


###############################################################################
# Cleanup debug files and conclude the process
# ~~~~~~~~~~~~
# Clean files in the mesh and log directories, print the process end message

cleanFilesExceptExtension(meshDirPath, ".h5")
cleanFilesExceptExtension(logDirPath, [".log", ".trn", ".bat"])

timeProcessEnd = datetime.now().strftime("%H:%M:%S")
print(
    colors.GREEN
    + f"[{timeProcessEnd}] Automatic meshing process completed!"
    + colors.RESET,
)
