# element_cfd-simulation
## Responsible: Giovanni Trovato
<img src="https://github.com/GiovanniTrovato.png" width="180">

## Background
Francesco Nori, Daniele Pucci and Silvio Traversaro have analized and simulated the Momentum Control of an Underactuated Flying Humanoid Robot in order to study the flight dynamics of iCub robot in orizzontal and vertical motions.
In those analysis the aerodynamic forces acting on the iCub robot are neglected. In order to decide if these forces can be neglected compared to other forces it will be useful to study, in the first analysis, the aerodynamic forces acting on a simple geometry.
After the meeting with Richard Browning we have set to start the complete simulation on a box (cube).  

## Objectives

### To estimate aerodynamic coefficients on the cube.
 With CFD analysies it will be possible to estimate lift and drag coefficients refer to the three main angles of rotation of the cube (Thinking about any geometry symmetries).

### To simulate the dynamics and aerodynamic forces together.
The objective is to implement aerodynamic coefficients in Gazebo software in order to obtain the best real simulation and valuate the effects of aerodynamic forces on the cube.

## Outcomes

### To neglect aerodynamic forces
Depending on the results obtained from these first analysis/simulations it will be possible to estimate the “weight” of the aerodynamic forces compared to the dynamic forces in the cube's matter. It will be a first good answer in order to carry on the CFD analysis on the Flying iCub.

### To use CFD simulations on the Flying iCub
The iCub is made by more components. The next step is to estimate the lift and drag coefficients on any component of iCub, as made with the cube on this element.

## Tasks
To achieve the above objectives, I have to accomplish the following tasks.

### Define the shape of the object.
Each aerodynamic coefficient is related to the object's shape, therefore it is important to define the shape and the sizes of the cube before acting the CFD analysis.

### Look for a good CFD software.
The main problem of this element is finding as much as possible the best CFD software. This software should be able to calculate the lift and drag coefficients in a fast way and obtain the best accurate and reliable results.

### Calculate the aerodynamic coefficients.
After finding out more about the chosen software, the next step is to estimate any aerodynamics coefficients on the cube. We want to find the values of lift and drag coefficients depending on the three main angles.

### Simulate with Gazebo.
Once we have the coefficients we will be able to include the aerodynamic forces in Gazebo software. The simulations, seen with Gazebo, will give us some important results to understand the current scale of values between dynamic and aerodynamic forces.

### Implement on iCub’s components.
If the simulations give us informations about a not negligible of aerodynamic forces we can carry on to find the aerodynamic coefficients on any component of iCub. This topic and these informations will be dealt with at the end of this element.

# Remarks
## CAD models
The CAD models in this repository have been designed using [PTC Creo](https://www.ptc.com/en/products/cad/creo). Refer to [this guide](https://github.com/loc2/loc2-commons/wiki/Setup-PTC-Creo) to configure the shared libraries (e.g. for commercial components).

## Git LFS remark
This repository exploits the Git Large File Support ([LFS][1]) to handle the binary files (e.g. PTC Creo and PDF files). To download the binary files, follow the GitHub [instructions][2].

[1]:https://git-lfs.github.com/
[2]:https://help.github.com/articles/installing-git-large-file-storage/
