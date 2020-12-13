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
The objective is to implement aerodynamic coefficients in Gazebo software in order to obtain the best real simulation and valuate the effects of aerodynamic forces on the iCub.

## Outcomes

### To neglect aerodynamic forces
Depending on the results obtained from these first analysis/simulations it will be possible to estimate the “weight” of the aerodynamic forces on single iCub parts compared to the dynamic forces. It will be a first good answer in order to carry on the CFD analysis on the Flying iCub.

### To use CFD simulations on the Flying iCub
The next step is to estimate the lift and drag coefficients on the complete iCub, verifying if it matches the sum of the single parts aerodynamic forces allowing the use of the superposition method or not.

## Tasks
To achieve the above objectives, I have to accomplish the following tasks.

### Perform the first simulations.
The first step is to estimate all the aerodynamic coefficients on the iCub parts. We want to find the values of lift and drag coefficients depending on the angle of attack and the sideslip angle for different values of freestream speed. To have more precise results we will start on simple 3D shapes similar to the different parts.

### Simulate the flow on the whole robot.
In this second phase we will do as before but using the complete robot. So we will extract all the aerodynamic forces and moments coefficients acting on the robot and we will evaluate if it is possible to use the superposition method, even if it is only possible for particular configurations with minimal wake interaction between the different parts of the robot.

### Simulate with Gazebo.
Once we have the coefficients we will be able to include the aerodynamic forces in Gazebo software. The simulations, seen with Gazebo, will give us some important results to understand the current scale of values between dynamic and aerodynamic forces.

# Remarks
## CAD models
The CAD models in this repository have been designed using [PTC Creo](https://www.ptc.com/en/products/cad/creo). Refer to [this guide](https://github.com/loc2/loc2-commons/wiki/Setup-PTC-Creo) to configure the shared libraries (e.g. for commercial components).

## Git LFS remark
This repository exploits the Git Large File Support ([LFS][1]) to handle the binary files (e.g. PTC Creo and PDF files). To download the binary files, follow the GitHub [instructions][2].

[1]:https://git-lfs.github.com/
[2]:https://help.github.com/articles/installing-git-large-file-storage/
