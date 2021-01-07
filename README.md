# element_cfd-simulation

## Responsible 

Antonello Paolino     |
:-------------------------:|
<img src="https://user-images.githubusercontent.com/75119799/102009876-b3456880-3d3a-11eb-9504-b17b59327a81.jpg" width="180"> |  

## Background
Francesco Nori, Daniele Pucci and Silvio Traversaro have analized and simulated the Momentum Control of an Underactuated Flying Humanoid Robot in order to study the flight dynamics of iCub robot in horizontal and vertical motions.
In those analysis the aerodynamic forces acting on the iCub robot are neglected. In order to decide if these forces can be neglected compared to other forces it will be useful to study, in the first analysis, the aerodynamic forces acting on simple geometries.
Previous work underlined the importance to establish a correct numerical method and a properly made discretization of the flow domain to have accurate results by the numerical simulations, in addition the software Ansys Fluent has been chosen to run the CFD analisys.
The final stage of this work will be the analysis of the aerodynamics of the complete iCub robot.

## Objectives
 
### To estimate aerodynamic coefficients on iCub robot different parts.
With CFD analysis it will be possible to estimate lift and drag coefficients relative to the different rotation angles of the iCub parts separated.

### To estimate aerodynamic coefficients on the complete iCub robot.
The same as before can be done on the complete iCub robot estimating the aerodynamic forces acting on it.

### To simulate the dynamics and aerodynamic forces together.
The objective is to implement aerodynamic coefficients in Gazebo software in order to obtain the best real simulation and evaluate the effects of aerodynamic forces on the iCub.

## Outcomes

### To estimate aerodynamic forces
Depending on the results obtained from these first analysis/simulations it will be possible to estimate the “weight” of the aerodynamic forces on single iCub parts compared to the dynamic forces. It will be a first good answer in order to carry on the CFD analysis on the Flying iCub.

### To use CFD simulations on the Flying iCub
The next step is to calculate the lift and drag coefficients on the complete iCub, comparing the results to similar objects and verifying if it matches the sum of the single parts aerodynamic forces allowing the use of the superposition method or not.

## Milestones

### Perform the first simulations on iCub parts.
The first milestone is to estimate the aerodynamic coefficients on the iCub parts. We want to find the values of lift and drag coefficients depending on the angle of attack and the sideslip angle for different values of freestream speed. This will be achieved starting from simple 3D shapes similar to the different parts to quickly set up the input of the analysis.

### Simulate the flow on a simplified model of the complete iCub robot.
This milestone will require different steps from the creation of the simplified model of the complete robot (using spheres, cilinders and simple shapes for the parts) to the CFD simulations. The results at this point will give a better estimate of the forces and moments acting on the iCub. 

### Simulate the flow on the whole robot.
The last challenge will be the integration of the iCub geometry in the CFD solver to do the simulations and extract all the aerodynamic forces and moments coefficients as functions of the main angles to build an aerodynamic database.

### Simulate with Gazebo.
This milestone will be a further step to integrate the aerodynamic model in the flight simlations to make the robot stable and controllable during all the phases of the mission.

# Remarks
## CAD models
The CAD models in this repository have been designed using [PTC Creo](https://www.ptc.com/en/products/cad/creo). Refer to [this guide](https://github.com/loc2/loc2-commons/wiki/Setup-PTC-Creo) to configure the shared libraries (e.g. for commercial components).

## Git LFS remark
This repository exploits the Git Large File Support ([LFS][1]) to handle the binary files (e.g. PTC Creo and PDF files). To download the binary files, follow the GitHub [instructions][2].

[1]:https://git-lfs.github.com/
[2]:https://help.github.com/articles/installing-git-large-file-storage/
