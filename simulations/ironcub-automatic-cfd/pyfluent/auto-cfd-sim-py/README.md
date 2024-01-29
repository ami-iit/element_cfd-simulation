## Intro

This folder contains the necessary files and scripts to implement the automatic cfd simulations using [**`pyFluent`**](https://fluent.docs.pyansys.com/version/stable/) packages:

* [`ansys-fluent-core`](https://github.com/ansys/pyfluent)
* [`ansys-fluent-parametric`](https://github.com/ansys/pyfluent-parametric)
* [`ansys-fluent-visualization`](https://github.com/ansys/pyfluent-visualization)


## Prepare the files

* **`case`**: put in this folder the case files (`.cas.h5`) generated before for the robot in the nominal configuration (file name = configuration name) and for $(\alpha=0^\circ;\beta=0^\circ)$
* **`data/outputParameters`**: setup the file such that the first line contains in order the input parameters name followed by the report definition names to be computed as simulation output
* **`src`**: insert the configurations to be tested in the `jointConfig.csv` file following the file formatting, then also the pitch and yaw angles in `pitchAngles.csv`, `yawAngles.csv` and `yawAnglesStart.csv` (this last one is only valid for the first simulation cycle, in case the previous process failed before finishing the simulations for a configuration)


## How to run the code

Run **`src/runSim.py`** python script inside the environment created using `mamba` packages.
Have fun!

## Output files

In `data` you can find:
* `outputParameters` filled with all the aerodynamic force areas data
* `pressures` repo containing the prssure distribution data from all the simulations
* `contours` repo containing all the longitudinal plane contours of velocity magnitude (as a check)
* `residuals` repo containing the resiudals for all the simulations (as a check)

