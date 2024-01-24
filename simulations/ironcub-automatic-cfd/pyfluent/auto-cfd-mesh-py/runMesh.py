'''
Author: Antonello Paolino
Date: 2013-06-10
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

######################### SIMULATION SETTINGS ##################################
core_number         = 16        # number of cores to use (only pre-post mode if gpu is True)
use_gpu             = True      # use GPU native solver
iteration_number    = 1000      # number of iterations to run in the solver

################################# PATHS DEFINITION ############################## 
# Define root folder path
rootPath = pathlib.Path(__file__).parents[0]

# Define case, data, source and log directory paths
caseDirPath = rootPath / "case" # Fluent case directory path
dataDirPath = rootPath / "data" # data directory path
srcDirPath  = rootPath / "src"  # source directory path
logPath     = rootPath / "log"  # log directory path

# Define file names
pitchAnglesFileName    = "pitchAngles.csv"
yawAnglesStartFileName = "yawAnglesStart.csv"
yawAnglesFileName      = "yawAngles.csv"
jointConfigFileName    = "jointConfig.csv"
outputParamFileName    = "outputParameters.csv"

# Define file paths
pitchAnglesFilePath    = srcDirPath / pitchAnglesFileName       # pitch angles file path
yawAnglesStartFilePath = srcDirPath / yawAnglesStartFileName    # yaw angles start file path
yawAnglesFilePath      = srcDirPath / yawAnglesFileName         # yaw angles file path
jointConfigFilePath    = srcDirPath / jointConfigFileName       # joint configuration file path
outputParamFilePath    = dataDirPath / outputParamFileName      # output parameters file path

# create data directories if not exists
dataDirectories = ["residuals", "contours", "pressures"]

for directory in dataDirectories:
    directoryPath = dataDirPath / directory
    if not directoryPath.exists():
        directoryPath.mkdir()
        print(f"Creating {directory} directory: '{directoryPath}'.")
    else:
        print(f"{directory} directory: '{directoryPath}'.")

# Define residuals, contours and pressures paths
residualsPath = dataDirPath / dataDirectories[0]
contoursPath  = dataDirPath / dataDirectories[1]
pressuresPath = dataDirPath / dataDirectories[2]

######################### PROCESS PARAMETERS LOADING ############################
# Load pitch angles from file
with open(str(pitchAnglesFilePath), 'r') as pitchAngleCSV:
    pitchAngleFile      = pitchAngleCSV.readlines()
    pitchAngleString    = pitchAngleFile[0]
    pitchAngleListStr   = pitchAngleString[:-1].split(',')
    pitchAngleList      = [float(pitchAngleStr) for pitchAngleStr in pitchAngleListStr]

# Load yaw angles for start configuration from file
with open(str(yawAnglesStartFilePath), 'r') as yawAngleStartCSV:
    yawAngleStartFile       = yawAngleStartCSV.readlines()
    yawAngleStartString     = yawAngleStartFile[0]
    yawAngleStartListStr    = yawAngleStartString[:-1].split(',')
    yawAngleStartList       = [float(yawAngleStartStr) for yawAngleStartStr in yawAngleStartListStr]

# Load yaw angles for successive configurations from file
with open(str(yawAnglesFilePath), 'r') as yawAngleCSV:
    yawAngleFile    = yawAngleCSV.readlines()
    yawAngleString  = yawAngleFile[0]
    yawAngleListStr = yawAngleString[:-1].split(',')
    yawAngleList    = [float(yawAngleStr) for yawAngleStr in yawAngleListStr]

# Load output parameters from file
with open(str(outputParamFilePath), 'r') as outputParamCSV:
    outputParameterFile   = outputParamCSV.readlines()
    outputParameterList   = outputParameterFile[0][:-1].split(',')
    outputParameterList   = outputParameterList[3:]
    
# Load robot joint config names
with open(str(jointConfigFilePath), 'r') as jointConfigCSV:
    jointConfigFile  = jointConfigCSV.readlines()
    jointConfigNames = []
    for jointConfig in jointConfigFile:
        temp = jointConfig[:-1].split(',')
        jointConfigNames.append(temp[0])
    
################################# MPI OPTION ####################################
# this fixes the MPI error on Linux setting MPI to openmpi (needed for the ws)
if os.name == "posix":
    mpi_option = "-mpi=openmpi"
else:
    mpi_option = ""

############################## Start the automatic process ########################
jointConfigIndex = 0
# Cycle on the configurations
for jointConfigName in jointConfigNames:

    # Define Fluent case file and path for current configuration 
    caseFileName = jointConfigName + ".cas.h5"      # Fluent jointConfig case file name
    caseFilePath = caseDirPath / caseFileName       # Fluent jointConfig case file full path

    # Define list of yaw angles (different for first config to restart a crushed process)
    yawAngleCycleList = yawAngleStartList if jointConfigIndex == 0 else yawAngleList
    
    ####################### Launch Fluent session via pyFluent #######################
    timeFluentStart = datetime.now().strftime("%H:%M:%S")
    print(f"[{timeFluentStart}] Starting pyFluent session...")
    solver = pyfluent.launch_fluent(
        mode="solver",                      # "meshing", "pure-meshing" or "solver"
        precision="double",                 # single or double precision
        version="3d",                       # 2d or 3d Fluent version
        processor_count=core_number,        # number of processors (only pre-post mode if gpu is True)
        gpu=use_gpu,                        # use GPU native solver
        start_transcript=False,             # start transcript file
        cwd=str(logPath),                   # working directory
        show_gui=False,                     # show GUI or not
        additional_arguments=mpi_option)    # additional arguments (used for MPI option)

    # Start the cycle for different yaw angles
    for yawAngle in yawAngleCycleList:

        # Singular configuration check: |yawAngle| == 90 => wind direction not changing with pitch angle
        pitchAngleCycleList = pitchAngleList if ( abs(abs(yawAngle) - 90) > 1e-4 ) else [0.0]

        # Start the cycle for different pitch angles
        for pitchAngle in pitchAngleCycleList:

            ################################# pyFluent run ##################################
            # Read the case file
            solver.file.read_case(file_name=str(caseFilePath))
            
            # Rotate the mesh
            solver.mesh.rotate(angle=np.deg2rad(pitchAngle), origin=[0, 0, 0], axis_components=[-1, 0, 0])
            solver.mesh.rotate(angle=np.deg2rad(yawAngle), origin=[0, 0, 0], axis_components=[0, 1, 0])

            # Set the correct BC (Boundary Conditions)
            solver.tui.mesh.modify_zones.sep_face_zone_mark("inlet", "region_in", "yes")    # separate external surface ("inlet)") according to face cell zone (region_in: Z >= -1[m])
            solver.tui.mesh.modify_zones.zone_type("inlet", "pressure-outlet")              # change new "inlet" zone to pressure-outlet BC type ("inlet:001" will stay inlet BC type)

            # Initialize and run flow solver
            solver.solution.initialization.initialize()
            solver.solution.run_calculation.iterate(iter_count=iteration_number)

            ################### pyFluent post (no pyfluent-visualization) ###################

            # plot and save residuals
            solver.tui.plot.residuals("y y y y y y")                        # plot residuals (y:yes; n:no; for each residual)
            solver.tui.display.set.picture.driver.jpeg()                    # set picture driver to jpeg
            solver.results.graphics.picture.use_window_resolution = False   # use window resolution
            solver.results.graphics.picture.x_resolution = 1920             # set picture x resolution
            solver.results.graphics.picture.y_resolution = 1440             # set picture y resolution
            solver.tui.display.save_picture(str(residualsPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}"))
            # solver.results.graphics.picture.save_picture(str(residualsPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}")) not working

            # plot and save velocity magnitude contour on YZ plane
            solver.results.graphics.contour.display(object_name = "velocity-magnitude-contour")
            solver.results.graphics.views.restore_view(view_name = "right")
            solver.results.graphics.picture.use_window_resolution = False   # use window resolution
            solver.results.graphics.picture.x_resolution = 1920             # set picture x resolution
            solver.results.graphics.picture.y_resolution = 1440             # set picture y resolution
            solver.tui.display.save_picture(str(contoursPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}"))
            # solver.results.graphics.picture.save_picture(str(contoursPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}")) not working

            ################################## Export force report values ##################################        
            outputParameterValueList = solver.solution.report_definitions.compute(report_defs=outputParameterList)

            with open(str(outputParamFilePath), 'a') as outputParamCSV:
                outputParameterString  = f"{jointConfigName},{pitchAngle},{yawAngle}"
                outputParameterCounter = 0
                for outputParameter in outputParameterList:
                    outputParameterValue = outputParameterValueList[outputParameterCounter][outputParameterList[outputParameterCounter]][0]
                    outputParameterString  = outputParameterString + f",{outputParameterValue}"
                    outputParameterCounter += 1
                outputParamCSV.writelines(outputParameterString+"\n")
            
            ################################## Export pressures ##################################
            solver.results.graphics.vector["velocity_vector_symmetry"] = {}
            surfaceNameList = solver.results.graphics.vector["velocity_vector_symmetry"].surfaces_list()
            for surfaceName in surfaceNameList:
                pressFilePath = str(pressuresPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}-{surfaceName}.txt")
                solver.file.export.ascii(name = pressFilePath, surface_name_list = [surfaceName], delimiter = "space", cell_func_domain = ["pressure"], location = "node")
            
            # Export single pressure data (useless for now, but it can be enhanced someway later)
            # pressFilePath = str(pressuresPath / f"{jointConfigName}-{int(pitchAngle)}-{int(yawAngle)}.txt")
            # solver.file.export.ascii(name = pressFilePath, surface_name_list = surfaceNameList, delimiter = "space", cell_func_domain = ["pressure"], location = "node")
            
            # Print iteration end message
            timeIterEnd = datetime.now().strftime("%H:%M:%S")
            print(f"[{timeIterEnd}] Iter for {jointConfigName}, alpha={pitchAngle}, beta={yawAngle}: Success!")
    
    jointConfigIndex += 1
    # Close the solver process
    solver.exit()
    timeJointConfigEnd = datetime.now().strftime("%H:%M:%S")
    print(f"[{timeJointConfigEnd}] {jointConfigName} iterations completed!")

timeProcessEnd = datetime.now().strftime("%H:%M:%S")
print(f"[{timeProcessEnd}] Automatic CFD process completed successfully!")