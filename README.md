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

### To evaluate the different turbulence models
Since the problem deals with the aerodynamics of a bluff body as the iRonCub is, it's fundamental to determine which turbulence model returns the best results in terms of forces and moments prediction accuracy and computational cost.

### To estimate aerodynamic coefficients on iRonCub robot different parts.
With CFD analysis it will be possible to estimate aerodynamic forces and moments relative to the different rotation angles of the iCub parts separated.

### To estimate aerodynamic forces on the complete iRonCub robot.
The same as before can be done on the complete iRonCub robot estimating the aerodynamic forces acting on it.

## Outcomes

### To estimate aerodynamic forces
Depending on the results obtained from these first analysis/simulations it will be possible to estimate the “weight” of the aerodynamic forces on single iCub parts compared to the dynamic forces. It will be a first good answer in order to carry on the CFD analysis on the Flying iCub.

### To use CFD simulations on the flying iRonCub
The next step is to calculate the aerodynamic forces on the complete iRonCub, comparing the results to similar objects and verifying if it matches the sum of the single parts aerodynamic forces allowing the use of the superposition method or not (given the strong wake interations between the different parts we expect the superposition to be useless for this kind of problem).

## Milestones

### [Validate the numerical model](https://github.com/dic-iit/element_cfd-simulation/issues/71)
The first milestone involves the validation of the numerical method and the turbulence model on a simple 3D object such as a sphere, to compare results between numrical simulations and experiments in order to calibrate the simulation parameters to match the different outcomes. In this phase a strong correlation between literature and analysis should be found.

### [Perform the first simulations on iCub parts](https://github.com/dic-iit/element_cfd-simulation/issues/67)
This milestone is to estimate the aerodynamic coefficients on the iCub parts. We want to find the values of lift and drag coefficients, but the most important outcomes of this analysis will be the investigations on the flow field characteristics in order to decide which numerical model best represents the physical behavior of the flow around the different parts. In particular a main focus is on the influence of interaction between transition and separation on the aerodynamic forces values.

### Simulate the flow on a simplified model of iRonCub.
This milestone will provide a first acceptable qualitative result on the real aerodynamic forces acting on iRonCub during flight: it will account for the interaction between different parts and the geometry will be close to the real one (considering that the external surfaces will be very close to the real ones and only the internal parts and the link geometries will be neglected for this analysis). The main effort for this step will be the generation of a proper mesh for the turbulence model selected. 

### Simulate the flow on the iRonCub.
The last challenge will be the integration of the iRonCub geometry in the CFD solver to do the simulations and extract all the aerodynamic forces and moments coefficients as functions of the main angles to build an aerodynamic database. In particular it will be also important to understand if a more detailed model of iRonCub gives a relevant increase in aerodynamic forces prediction accuracy or if it adds only computational cost and meshing issues (linked to the more complex geometries).

# Remarks
## CAD models
The CAD models in this repository have been designed using [PTC Creo](https://www.ptc.com/en/products/cad/creo). Refer to [this guide](https://github.com/loc2/loc2-commons/wiki/Setup-PTC-Creo) to configure the shared libraries (e.g. for commercial components).

## Git LFS remark
This repository exploits the Git Large File Support ([LFS][1]) to handle the binary files (e.g. PTC Creo and PDF files). To download the binary files, follow the GitHub [instructions][2].

[1]:https://git-lfs.github.com/
[2]:https://help.github.com/articles/installing-git-large-file-storage/
