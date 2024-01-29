## `ironcub-automatic-cfd`

In this repo you can find the 2 different methods used to automatize the process to generate cfd simulations on iRonCub robot: **Automatic _Workbench_ routine** and **Automatic _pyFluent_ routine**

### Automatic _Workbench_ routine (`workbench`)

This routine is based on the execution of the whole process only using _ANSYS Workbench_ automatic scripts.


### Automatic _pyFluent_ routine (`pyfluent`)

This routine automatically modifies the geometry using _ANSYS Workbench_ automatic scripts (at the moment), but performs the meshing and simulation steps using `pyFluent` (the _Fluent API_ for python).
