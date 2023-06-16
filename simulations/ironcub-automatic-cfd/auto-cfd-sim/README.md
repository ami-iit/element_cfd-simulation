## `auto-cfd-sim`

### Intro

This repo contains the files for performing the second pipeline part which consists in loading the _ANSYS Fluent_ case files and performing the CFD simulations on the robot selected joints configurations for different pitch and yaw angles. The resulting computed aerodynamic force coefficients on the robot links are reported then in a dedicated file.


### Files

Here is an overview of the input files necessary for performing the automatic steps in `ANSYS Workbench 2023R1`. Please be aware that the process could not work on different versions of the software (in particular previous versions).


* **`root`**

    - **`auto_cfd_sim.wbpj`**: this is the _ANSYS Workbench_ main project which contains all the necessary components to be automatized by the script to obtain the automatic simulations routine.

    - **`auto-cfd-sim-script.wbjn`**: this is the main script which hold on the whole iterative structure of the automatic process, reading the input files and generating the desired output.


* **`case`**

    In this repo all the _ANSYS Fluent_ case files (`.cas`) from previous pipeline part have to be copied to be used as input for this pipeline part.

* **`src`**
    - **`jointConfig.csv`**: this is a `.csv` file containing the robot joints positions in the standard order (same as all `iCub` robots, ankles pitch and roll excluded); each row is a different robot joints configuration to be generated, starting with the configuration name and following with the joint angles in `deg`, here there is an example of the file:

        ```py
        hovering,0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight30,0.0,0.0,0.0,-40.7,11.3,26.5,58.3,-40.7,11.3,26.5,58.3,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight50,0.0,0.0,0.0,-31.3,19.0,26.3,45.3,-31.3,19.0,26.3,45.3,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight60,0.0,0.0,0.0,-25.0,24.0,30.0,35.0,-25.0,24.0,30.0,35.0,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0

        ```
    - **`pitchAngles.csv`** and **`yawAngles.csv`**: these are the `.csv` files which contain the pitch and yaw angles (expressed in `deg` units) to be simulated (pitch angles are performed for each yaw angle); the angles should have no spaces in their definitions and an empty line should be left at the end of the file. The range for pitch angles is $\alpha \in [0^\circ;180^\circ]$ while for yaw angles is $\beta \in (-180^\circ;180^\circ]$

        Example of a **`pitchAngles.csv`** file:
        ```py
        0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180

        ```
        Example of a **`yawAngles.csv`** file:
        ```py
        -160,-140,-120,-100,-80,-60,-40,-20,0,20,40,60,80,100,120,140,160,180

        ```

* **`data`**
    - **`outputParameters.csv`**: this file contains all the results of the aerodynamic coefficients calculated on the different robot links;
    - **`contours`**: this repo stores all the YZ plane contours of the flow field to check the correct setting of boundary conditions;
    - **`residuals`**: this repo stores the scaled residuals plots for each simulation to chck for problems in the simulation convergence whenever the data would appear not coherent with itself.


### Code theory clarification

* `attitude singularities`
    The attitude angles rotations aforementioned introduce some configurations (for $\beta=\pm 90^\circ$ yaw angles) in which for different angles of attack the relative velocity has the same direction resulting in the same configuration with just rotated forces; therefore the code doesn't cycle on these yaw angles but just does one simulation to save time!


* `aerodynamic coefficients`
    The aerodynamic force coefficients are computed using the generic formula $C_F = \frac{2\cdot F}{\rho V^2 A}$ where the air density $\rho=1.225\ kg/m^3$ and reference area $A=1\ m^2$ are constant. For the aerodynami torque coefficents $C_M = \frac{2\cdot M}{\rho V^2 A L}$ where the only difference is the constant reference length $L=1\ m$ has been used. The unit reference length and area have been used as often done in literature for bluff bodies such as the robot.


### How to use the code

* open the **`auto_cfd_sim.wbpj`** project file;
* update the **`auto-cfd-sim-script.wbjn`** `dirPath` variable with the complete path to the project repo (e.g. ```dirPath = C:/.../auto-cfd-model/```);
* update **`jointConfig.csv`** file with the joints configurations to be simulated (**IMPORTANT**: leave a final empty line for the correct formatting of the last joint angles and be sure that all the joints configurations have a relative `.cas` file in the **`case`** repo);
* update **`pitchAngles.csv`** and **`yawAngles.csv`** with the pitch and yaw angles to be performed, according to the previously defined guidelines (e.g. leaving an extra empty line for correct data formatting);
* run the **`auto-cfd-sim-script.wbsc`** _ANSYS Workbench_ script and wait until all the simulations are performed, the results will gradually appear in the **`outputParameters.csv`** files.