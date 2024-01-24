## `ironcub-automatic-cfd`

In this repo you can find the 2 different methods used to automatize the process to generate cfd simulations on iRonCub robot: **Automatic _Workbench_ routine** and **Automatic _pyFluent_ routine**

### Automatic _Workbench_ routine (`workbench`)

This routine is based on the execution of the whole process only using _ANSYS Workbench_ automatic scripts.


### Automatic _pyFluent_ routine (`pyfluent`)

This routine automatically modifies the geometry using _ANSYS Workbench_ automatic scripts (at the moment), but performs the meshing and simulation steps using `pyFluent` (the _Fluent API_ for python).




In this repo the automatic cfd pipeline parts are stored, after splitting the proces in 2 main parts collected in the 2 repos you can find here.

* **`auto-cfd-model`**: in this repo you can find the first pipeline part, taking as input the robot joint configurations, the geometry files and the output parameters file; then the geometry is automatically updated and the mesh is generated, creating a ready _ANSYS Fluent_ `.cas` file to be used as input of the second pipeline part;

* **`auto-cfd-sim`**: in this repo the input are the `.cas` file from the first pipeline part, the pitch and yaw angles and the output parameters file; the operations inside `ANSYS Fluent` allow to change pitch and yaw angles and then perform the simulations collecting th data on the whole-body aerodynamic force coefficients.

* **`auto-cfd-sim-py`**: this repo encloses all the necessary files to perform automatic cfd simulations starting from already defined case files and puitch and yaw angles input files, the process is the same described in `auto-cfd-sim` but the main difference is that this routine doesn't rely on `ANSYS Workbench` automatic scripting features, but uses the new `pyfluent` packages which allow to use Fluent directly from command within a fully-integrated python code. This routine has 2 main advantages: 
  - `Native GPU Solver` available from `ANSYS Fluent` (not from `ANSYS Workbench`);
  - Easy to adapt to run on external workstations/servers after importing all the correct packages/files (or cloning the repo). 

More details regarding the 2 pipeline parts are described in the relative repos.
