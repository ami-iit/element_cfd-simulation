## `auto-cfd-model`

### Intro

This repo contains the files for performing the first pipeline part which consists in generating the _ANSYS Fluent_ mesh and setup for each robot joint configuration to be simulated.

### Files

Here is an overview of the input files necessary for performing the automatic steps in `ANSYS Workbench 2023R1`. Please be aware that the process could not work on different versions of the software (in particular previous versions).

* **`root`**

    - **`auto_cfd_model.wbpj`**: this is the _ANSYS Workbench_ main project which contains all the necessary components to be automatized by the script to obtain the automatic mesh and setup generation.

    - **`auto-cfd-model-script.wbjn`**: this is the main script which hold on the whole iterative structure of the automatic process, reading the input files and generating the desired output.


* **`src`**

    - **`jointConfig.csv`**: this is a `.csv` file containing the robot joints positions in the standard order (same as all `iCub` robots, ankles pitch and roll excluded); each row is a different robot joints configuration to be generated, starting with the configuration name and following with the joint angles in `deg`, here there is an example of the file:

        ```py
        hovering,0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight30,0.0,0.0,0.0,-40.7,11.3,26.5,58.3,-40.7,11.3,26.5,58.3,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight50,0.0,0.0,0.0,-31.3,19.0,26.3,45.3,-31.3,19.0,26.3,45.3,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0
        flight60,0.0,0.0,0.0,-25.0,24.0,30.0,35.0,-25.0,24.0,30.0,35.0,0.0,10.0,7.0,0.0,0.0,10.0,7. 00.0

        ```


    - **`outputParameters.csv`**: this file contains the lit of the output aerodynamic coefficient names which are required to the correct functioning of the project when automatically updated.


* **`geom`**

    - `ironcub-model-share.scdoc` and `iRonCub-share.scdoc`: these are the _SpaceClaim_ geometry assembly and iRonCub components files which contain the robot simplified geometry, surfaces and external boundaries _Named Selection_, and the definition of the _Script parameters_;

    - `ironcub-model-script.scscript`: this file contains the _SpaceClaim_ script which is used to automatically adjust the robot geometry according to the desired joint angles, this is performed using the _Script Parameters_ coming from the `Workbench` project and automatically modified from one iteration to the following one.


* **`case`**

    In this repo all the _ANSYS Fluent_ case files (`.cas`) are stored and then used as input for the second part of the pipeline.


### Code theory clarification

* `robot attitude rotation`
    The robot geometry is initialized with the `root_link` reference frame $(\mathcal{O}_{r})$ aligned with the wind frame $(\mathcal{O}_{w})$ which has the _z axis_ on the relative wind opposite direction, and the _y axis_ vertical pointing upward. This configuration is relative to attitude angles of $(\alpha,\beta)=(90^\circ,0^\circ)$ considering $\alpha=0^\circ$ when the robot vertical axis is opposite aligned to the relative wind direction. The attitude angle is obtained first rotating the geometry around its _y axis_ of a quantity equal to the yaw angle: $R_{y}(\theta);$ and then rotating the geometry on the new _x' axis_ of $90^\circ - \alpha$ to compensate for the initial misalignment of the robot: $R_{x'}(90^\circ - \alpha).$


### How to use the code

* open the **`auto_cfd_model.wbpj`** project file;
* update the **`auto-cfd-model-script.wbjn`** `dirPath` variable with the complete path to the project repo (e.g. ```dirPath = C:/.../auto-cfd-model/```);
* update **`jointConfig.csv`** file with the joints configurations (**IMPORTANT**: leave a final empty line for the correct formatting of the last joint angles);
* run the **`auto-cfd-model-script.wbsc`** _ANSYS Workbench_ script and wait until all the `.cas` files are generated in the `./case/` repo;
* copy-paste the case files in the **`case`** repo of **`../auto-cfd-sim/`** repo.