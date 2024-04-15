## Intro

This folder contains the necessary files and scripts to implement the automatic cfd meshing using [**`pyFluent`**](https://fluent.docs.pyansys.com/version/stable/) packages:

* [`ansys-fluent-core`](https://github.com/ansys/pyfluent)
* [`ansys-fluent-parametric`](https://github.com/ansys/pyfluent-parametric)
* [`ansys-fluent-visualization`](https://github.com/ansys/pyfluent-visualization)


## Prepare the files

* **`geom`**: put in this folder the geometry files (`.scdoc`) generated before for the robot in the nominal configuration (subrepo name = configuration name) for $(\alpha=0^\circ;\beta=0^\circ)$ (include both the `Geom.scdoc` and the `iRonCub-share.scdoc` files)
* **`data/outputParameters`**: setup the file such that the first line contains in order the input parameters name followed by the report definition names to be computed as simulation output
* **`src`**: insert the configurations to be tested in the `jointConfig.csv` file following the file formatting


## How to run the code

Run **`src/runMesh.py`** python script inside the environment created using `mamba` packages.
Have fun!


## Output data

In `case` you can find the generated `.cas` case and `.msh.h5` mesh files for each joint configuration.
 