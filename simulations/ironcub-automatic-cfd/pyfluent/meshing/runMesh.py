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
# Define directory and file paths
# ~~~~~~~~~~~~~
# Define the paths for the directories and the files used in the process.

# Define dir paths

rootPath = pathlib.Path(__file__).parents[0]

meshDirPath = rootPath / "mesh" / robotName[-3:] # mesh directory path
caseDirPath = rootPath / "case" / robotName[-3:] # Fluent case directory path
srcDirPath  = rootPath / "src"  # source directory path
logDirPath  = rootPath / "log"  # log directory path

parentPath = pathlib.Path(__file__).parents[1]

geomDirPath = parentPath / "geom" / robotName[-3:] # geometry directory path

# Define file paths

jointConfigFilePath = srcDirPath / f"jointConfig-{robotName[-3:]}.csv"  # joint configuration file path

###############################################################################
# Load joint configurations from files
# ~~~~~~~~~~~~~
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
            product_version="23.2.0",           # Fluent version
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
                "BOIFaceLabelList": robot.ironcubSurfacesList,
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
        # Pseudo-time solver: OFF

        solver.solution.methods.p_v_coupling.flow_scheme.set_state("Coupled")

        solver.solution.methods.warped_face_gradient_correction.enable(
            enable=True, gradient_correction_mode="memory-saving-mode"
        )
        
        solver.solution.methods.pseudo_time_method.formulation.coupled_solver.set_state("off")

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

        # define the reports for the surfaces
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
                cd.thread_names.set_state(reportSurfaceList)
                cd.force_vector.set_state([0, 0, -1])
                cd.average_over.set_state(100)
                # define surface cl report
                solver.solution.report_definitions.drag[reportDefName + "-cl"] = {}
                cl = solver.solution.report_definitions.drag[reportDefName + "-cl"]
                cl.thread_names.set_state(reportSurfaceList)
                cl.force_vector.set_state([0, 1, 0])
                cl.average_over.set_state(100)
                # define surface cs report
                solver.solution.report_definitions.drag[reportDefName + "-cs"] = {}
                cs = solver.solution.report_definitions.drag[reportDefName + "-cs"]
                cs.thread_names.set_state(reportSurfaceList)
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
        # Close Fluent, print an error message and skip the configuration.

        meshing.exit()

        timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
        print(
            colors.RED,
            f"[{timeJointConfigEnd}] {jointConfigName} mesh failed with the following error: \n",
            exceptionMessage,
            colors.RESET,
        )

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
