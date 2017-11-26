# element_cfd-simulation
## Responsible: Giovanni Trovato
<img src="https://github.com/GiovanniTrovato.png" width="180">

## Background
@francesconori @danielepucci @traversaro have analized and simulated the Momentum Control of an Underactuated Flying Humanoid Robot in order to study the flight dynamics of iCub robot in orizzontal and vertical motions.
In those analysis are neglected the aerodynamics forces acting on the Icub robot. In order to decide if these forces are currently neglected compared to other forces it will be useful to study, in the first analysis, the aerodynamics forces acting on a simple geometry. 
After the meeting with Richard Browning in IIT is been chosen a cube as simple geometry.  

## Objectives 

### To estimate aerodynamics coefficients on the cube.
 With CFD analyzies it will be possible to estimate lift and drag coefficients refer to the three main angles of rotation of the cube (Thinking about any geometry symmetries)
 
### To simulate the dynamics and aerodynamics forces together.
The objective is to implement aerodynamics coefficients in GAZEBO software in order to obtain the best real simulation and valuate the effects of aerodynamics forces on the cube.

## Outcomes

### To neglect aerodynamics forces
Depending on the results obtained from these first analizies/simulations it will be possible to estimate the “weight” of the aerodynamics forces compared to the dynamics forces in the cube's matter. It will be a first good answer in order to carry on the CFD analysis on the Flying Icub.

### To use CFD simulations on the Flying Icub
The iCub is made by more components. The next step is to estimate the lift and drag coefficients on any components of iCub, as made with the cube on this element. 

## Tasks
To achieve the above objectives, I have to accomplish the following tasks

### Define the shape of the object.
It is important to define the shape and the sizes of the cube before acting the analyzies.

### Look for a good CFD software.
The main problem of this element is finding as much as possible the best CFD software. This software should be fast to gain the lift and drag coefficients in order to obtain the best accurate and reliable results.

### Calculate the aerodynamics coefficients.
After finding out more about the chosen software, the next step is to estimate any aerodynamics coefficients on the cube. We want to find the values of lift and drag coefficients depending on the three main angles.

### Simulate with GAZEBO.
Once we have the coefficients we will be able to include the aerodynamics forces in GAZEBO software. The simulations, seen with Gazebo, will give us some important results to understand the current scale of values between dynamics forces and aerodynamics forces. 
### Implement on iCub’s components.
If the simulations give us informations about a not negligible of aerodynamics forces we can carry on to find the aerodynamics coefficients on any components of iCub. This topic and these informations will be dealt with at the end of this element.
