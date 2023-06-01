# ironcub-automatic-cfd

## Intro

The `automatic_cfd_project.wbpj` in this repo it's the main workbench project which processes the main **input parameters** and settings for performing automatic steps from geometry modification and meshing up to running the CFD simulations.
The output of the automatic process is a file containing the aerodynamic force and torque coefficients on all the robot links.

## Files

Here is an overview of the input files necessary for performing the automatic steps in `ANSYS Workbench 2023R1`. Please be aware that the process could not work on different versions of the software (in particular previous versions).


### Main

* `automatic-cfd-script.wbjn`
    This is the main script which hold on the whole iterative structure of the automatic process, reading the input files and generating the desired aerodynamic force and torque coefficients output file after each process iteration.  


### Input

* `jointConfig.csv`

    This is a `.csv` file containing the robot joints positions in the standard order (same as all `iCub` robots, ankles pitch and roll excluded); each row is a different robot joints configuration to be simulated, starting with the configuration name and following with the joint angles in `deg`, here there is an example of the file:

    ```py
    hovering,0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,10.0,7.0,0.0
    flight30,0.0,0.0,0.0,-40.7,11.3,26.5,58.3,-40.7,11.3,26.5,58.3,0.0,10.0,7.0,0.0,0.0,10.0,7.0,0.0
    flight50,0.0,0.0,0.0,-31.3,19.0,26.3,45.3,-31.3,19.0,26.3,45.3,0.0,10.0,7.0,0.0,0.0,10.0,7.0,0.0
    flight60,0.0,0.0,0.0,-25.0,24.0,30.0,35.0,-25.0,24.0,30.0,35.0,0.0,10.0,7.0,0.0,0.0,10.0,7.0,0.0

    ```

    It's important to ad a final empty line to this file for the correct formatting of the last joint configuration angles.



* `pitchAngles.csv` and `yawAngles.csv`

    These are the `.csv` files which contain the pitch and yaw angles (expressed in `deg` units) to be simulated (pitch angles are performed for each yaw angle); the angles should have no spaces in their definitions and an empty line should be left at the end of the file. The range for pitch angles is $\alpha \in [0^\circ;180^\circ]$ while for yaw angles is $\beta \in (-180^\circ;180^\circ]$

    Example of a `pitchAngles.csv` file:
    ```py
    0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180

    ```
    Example of a `yawAngles.csv` file:
    ```py
    -160,-140,-120,-100,-80,-60,-40,-20,0,20,40,60,80,100,120,140,160,180

    ```


* `ironcub-model-share.scdoc` and `iRonCub-share.scdoc`
    These are the _SpaceClaim_ geometry assembly and iRonCub components files which contain the robot simplified geometry, surfaces and external boundaries _Named Selection_, and the definition of the _Script parameters_;


* `ironcub-model-script.scscript`
    This file contains the _SpaceClaim_ script which is used to automatically adjust the robot geometry according to the desired attitude and joint angles, this is performed using the _Script Parameters_ coming from the `Workbench` project and automatically modified from one iteration to the following one.

### Output

* `outputParameters.csv`
    This file contains the simulation outputs in form of aerodynamic force and torque coefficients on the robot and its parts, other than the input used for the simulation (joint configuration name and attitude angles in `deg`) in order to be able to understand which is the real condition of the running case. An example of output file is reported here, with just the robot aerodynamic force coefficients, but it's possible to generalize it for every number of output coefficients just modifying the project and file formats:

    ```py
    "config","pitchAngle","yawAngle","ironcub-cd","ironcub-cl","ironcub-cs"
    hovering,0,0,0.089747718,0.00036872352,0.00038891436
    hovering,45,0,0.20430453,0.08193648,0.0010860447
    hovering,90,0,0.24183786,0.0085575692,-0.011719222
    hovering,0,90,0.16259752,-0.0064680343,-0.015659384
    flight30,0,0,0.11420436,0.0014176447,0.00018698685
    flight30,45,0,0.19762909,0.059124259,-0.0015711839
    flight30,90,0,0.22127596,0.018464575,-0.011155438
    flight30,0,90,0.17007302,0.0063315509,-0.021061339
    ```


## Code theory clarification

* `robot attitude rotation`
    The robot geometry is initialized with the `root_link` reference frame $(\mathcal{O}_{r})$ aligned with the wind frame $(\mathcal{O}_{w})$ which has the _z axis_ on the relative wind opposite direction, and the _y axis_ vertical pointing upward. This configuration is relative to attitude angles of $(\alpha,\beta)=(90^\circ,0^\circ)$ considering $\alpha=0^\circ$ when the robot vertical axis is opposite aligned to the relative wind direction. The attitude angle is obtained first rotating the geometry around its _y axis_ of a quantity equal to the yaw angle: $R_{y}(\theta);$ and then rotating the geometry on the new _x' axis_ of $90^\circ - \alpha$ to compensate for the initial misalignment of the robot: $R_{x'}(90^\circ - \alpha).$

* `attitude singularities`
    The attitude angles rotations aforementioned introduce some configurations (for $\beta=\pm 90^\circ$ yaw angles) in which for different angles of attack the relative velocity has the same direction resulting in the same configuration with just rotated forces; therefore the code doesn't cycle on these yaw angles but just does one simulation to save time!


* `aerodynamic coefficients`
    The aerodynamic force coefficients are computed using the generic formula $C_F = \frac{2\cdot F}{\rho V^2 A}$ where the air density $\rho=1.225\ kg/m^3$ and reference area $A=1\ m^2$ are constant. For the aerodynami torque coefficents $C_M = \frac{2\cdot F}{\rho V^2 A L}$ where the only difference is the constant reference length $L=1\ m$ has been used. The unit reference length and area have been used as often done in literature for bluff bodies such as the robot.