## `workbench`

In this repo the automatic cfd pipeline parts are stored, after splitting the proces in 2 main parts collected in the 2 repos you can find here.

* **`auto-cfd-model`**: in this repo you can find the first pipeline part, taking as input the robot joint configurations, the geometry files and the output parameters file; then the geometry is automatically updated and the mesh is generated, creating a ready _ANSYS Fluent_ `.cas` file to be used as input of the second pipeline part;

* **`auto-cfd-sim`**: in this repo the input are the `.cas` file from the first pipeline part, the pitch and yaw angles and the output parameters file; the operations inside `ANSYS Fluent` allow to change pitch and yaw angles and then perform the simulations collecting th data on the whole-body aerodynamic force coefficients.

More details regarding the 2 pipeline parts are described in the relative subdirectories.