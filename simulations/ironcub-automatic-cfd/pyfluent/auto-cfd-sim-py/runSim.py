"""
Author: Antonello Paolino
Date: 2024-02-28
Description:    This code uses the pyFluent packages to run iRonCub automatic CFD 
                simulations starting from properly defined case files.

This code is based on the examples provided at the following link: 
                
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

from src.utils import colors, getAnglesList, getOutputParameterList, getJointConfigNames

###############################################################################
# Set the Fluent configuration parameters
# ~~~~~~~~~~~~~
# Set the parameters for the Fluent session

core_number = 48        # number of cores (only pre-post if use_gpu=True)
use_gpu = False         # use GPU native solver
iteration_number = 1000 # number of iterations to run in the solver

# Set the MPI option for the WS
mpi_option = "-mpi=openmpi" if os.name == "posix" else ""


###############################################################################
# Define directory and file paths
# ~~~~~~~~~~~~~
# Define the paths for the directories and the files used in the process.

# Define dir paths

rootPath = pathlib.Path(__file__).parents[0]

caseDirPath = rootPath / "case"  # Fluent case directory path
dataDirPath = rootPath / "data"  # data directory path
srcDirPath = rootPath / "src"  # source directory path
logDirPath = rootPath / "log"  # log directory path

# Define file paths

pitchAnglesFilePath    = srcDirPath / "pitchAngles.csv"         # pitch angles file path
yawAnglesStartFilePath = srcDirPath / "yawAnglesStart.csv"      # yaw angles start file path
yawAnglesFilePath      = srcDirPath / "yawAnglesStart.csv"      # yaw angles file path
jointConfigFilePath    = srcDirPath / "jointConfig.csv"         # joint configuration file path
outputParamFilePath    = (dataDirPath / "outputParameters.csv") # output parameters file path

# Create data directories if not existing

dataDirectories = ["residuals", "contours", "pressures"]

for directory in dataDirectories:
    directoryPath = dataDirPath / directory
    if not directoryPath.exists():
        directoryPath.mkdir()
        print(
            colors.CYAN
            + f"[Message] Creating {directory} directory: '{directoryPath}'."
            + colors.RESET
        )
    else:
        print(
            colors.CYAN
            + f"[Message] {directory} directory: '{directoryPath}'."
            + colors.RESET
        )

# Define residuals, contours and pressures paths

residualsPath = dataDirPath / dataDirectories[0]
contoursPath  = dataDirPath / dataDirectories[1]
pressuresPath = dataDirPath / dataDirectories[2]

###############################################################################
# Load parameters from files
# ~~~~~~~~~~~~~
# Load the output parameters and the joint configuration names from the files.

pitchAngleList = getAnglesList(pitchAnglesFilePath)
yawAngleStartList = getAnglesList(yawAnglesStartFilePath)
yawAngleList = getAnglesList(yawAnglesFilePath)
outParamList = getOutputParameterList(outputParamFilePath)
jointConfigNames = getJointConfigNames(jointConfigFilePath)


###############################################################################
# Start the automatic process
# ~~~~~~~~~~~~~
# Start a cycle on all the provided joint configurations to run simulations for
# each of the loaded pitch and yaw angles.

for jointConfigIndex, jointConfigName in enumerate(jointConfigNames):

    # Define list of yaw angles (different for first config to restart a crushed process)

    yawAngleCycleList = yawAngleStartList if jointConfigIndex == 0 else yawAngleList

    ###############################################################################
    # Launch Fluent
    # ~~~~~~~~~~~~~
    # Launch Fluent as a service in meshing mode with double precision.

    timeFluentStart = datetime.now().strftime("%H:%M:%S")
    print(f"[{timeFluentStart}] Starting pyFluent session...")

    solver = pyfluent.launch_fluent(
        mode="solver",                      # "meshing", "pure-meshing" or "solver"
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
    # Start the cycle on yaw angles
    # ~~~~~~~~~~~~~
    # Start a cycle on all the yaw angles for each joint configuration to run.

    for yawAngle in yawAngleCycleList:

        # Singular configuration check:
        # |yawAngle| == 90 => wind direction not changing with pitch angle

        pitchAngleCycleList = pitchAngleList if ( abs(abs(yawAngle) - 90) > 1e-4 ) else [0.0]


        ###############################################################################
        # Start the cycle on pitch angles
        # ~~~~~~~~~~~~~
        # Start a cycle on all the pitch angles for each joint configuration to run.

        for pitchAngle in pitchAngleCycleList:

            ###############################################################################
            # Read the case file
            # ~~~~~~~~~~~~~
            # Read the case file for the current joint configuration

            caseFileName = jointConfigName + ".cas.h5"
            caseFilePath = caseDirPath / caseFileName
            solver.file.read_case(file_name=str(caseFilePath))


            ###############################################################################
            # Modify the mesh
            # ~~~~~~~~~~~~~
            # Rotate the mesh according to pitch and yaw angles and set the correct
            # Boundary Conditions.

            solver.mesh.rotate(
                angle=np.deg2rad(pitchAngle),
                origin=[0, 0, 0],
                axis_components=[-1, 0, 0],
            )

            solver.mesh.rotate(
                angle=np.deg2rad(yawAngle),
                origin=[0, 0, 0],
                axis_components=[0, 1, 0],
            )

            solver.tui.mesh.modify_zones.sep_face_zone_mark("inlet", "region_in", "yes")
            solver.tui.mesh.modify_zones.zone_type("inlet", "pressure-outlet")


            ###############################################################################
            # Initialize flow field
            # ~~~~~~~~~~~~~~~~~~~~~
            # Initialize the flow field using hybrid initialization.

            solver.solution.initialization.hybrid_initialize()


            ###############################################################################
            # Solve the flow field
            # ~~~~~~~~~~~~~~~~~~~~~~~~
            # Solve the flow field for the current joint configuration and angles.

            solver.solution.run_calculation.iterate(iter_count=iteration_number)


            ###############################################################################
            # Plot and save residuals
            # ~~~~~~~~~~~~~~~~~~~~~~~~
            # Plot and save the residuals for the current joint configuration and angles.

            solver.tui.plot.residuals("y y y y y y")
            solver.tui.display.set.picture.driver.jpeg()
            solver.results.graphics.picture.use_window_resolution = False
            solver.results.graphics.picture.x_resolution = 1920
            solver.results.graphics.picture.y_resolution = 1440

            solver.tui.display.save_picture(
                str( residualsPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}" )
            )

            # The designed command was not working:
            # solver.results.graphics.picture.save_picture(
            #     str(residualsPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}")
            #     )


            ###############################################################################
            # Plot and save contours
            # ~~~~~~~~~~~~~~~~~~~~~~~~
            # Plot and save the velocity magnitude contour on the yz plane.

            solver.results.graphics.contour["velocity-contour"] = {}

            solver.results.graphics.contour["velocity-contour"] = {
                "field": "velocity-magnitude",
                "surfaces_list": ["yz_plane"],
                "node_values": True,
                "range_option": {
                    "option": "auto-range-on",
                    "auto_range_on": {"global_range": False},
                },
            }
            solver.results.graphics.contour.display(object_name="velocity-contour")
            solver.results.graphics.views.restore_view(view_name="right")
            solver.results.graphics.picture.use_window_resolution = False
            solver.results.graphics.picture.x_resolution = 1920
            solver.results.graphics.picture.y_resolution = 1440

            solver.tui.display.save_picture(
                str( contoursPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}" )
            )

            # The designed command was not working:
            # solver.results.graphics.picture.save_picture(
            #     str( contoursPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}" )
            # )


            ###############################################################################
            # Compute and write output parameters
            # ~~~~~~~~~~~~~~~~~~~~~~~~
            # Compute and write the output parameters

            outParamValList = solver.solution.report_definitions.compute(
                report_defs=outParamList
            )

            with open(str(outputParamFilePath), "a") as outputParamCSV:

                outputParameterString = f"{jointConfigName},{pitchAngle},{yawAngle}"

                for outParamIndex, _ in enumerate(outParamList):

                    outParamVal = outParamValList[outParamIndex][outParamList[outParamIndex]][0]
                    outputParameterString = outputParameterString + f",{outParamVal}"

                outputParamCSV.writelines(outputParameterString + "\n")


            ###############################################################################
            # Export pressure data
            # ~~~~~~~~~~~~~~~~~~~~~~~~
            # Export the pressure data on each single surface.

            cd_report = solver.solution.report_definitions.drag["ironcub-cd"]
            surfaceNameList = cd_report.thread_names.allowed_values()

            for surfaceName in surfaceNameList:
                pressFileName = f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}-{surfaceName}.prs"
                pressFilePath = str( pressuresPath / pressFileName )
                solver.file.export.ascii(
                    name=pressFilePath,
                    surface_name_list=[surfaceName],
                    delimiter="space",
                    cell_func_domain=["pressure"],
                    location="node",
                )


            ###############################################################################
            # Print Iter End message
            # ~~~~~~~~~~~~
            # Print the end message for the current pitch and yaw angles.

            timeIterEnd = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{timeIterEnd}] Iter for {jointConfigName}, alpha={pitchAngle}, beta={yawAngle}: Success!"
            )

    ###############################################################################
    # Close Fluent Solver Session
    # ~~~~~~~~~~~~
    # Close Fluent solver session and print the end message for the current
    # configuration.

    solver.exit()

    timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
    print(
        colors.GREEN,
        f"[{timeJointConfigEnd}] {jointConfigName} iterations completed!",
        colors.RESET,
    )


###############################################################################
# Cleanup debug files and conclude the process
# ~~~~~~~~~~~~
# Clean files in the mesh and log directories, print the process end message

# TODO: add debug files cleanup

timeProcessEnd = datetime.now().strftime("%H:%M:%S")
print(
    colors.GREEN,
    f"[{timeProcessEnd}] Automatic CFD process completed successfully!",
    colors.RESET,
)
