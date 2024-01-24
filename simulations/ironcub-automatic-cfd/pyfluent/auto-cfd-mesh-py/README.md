## Intro

This folder contains the necessary files and scripts to implement the automatic cfd meshing using [**`pyFluent`**](https://fluent.docs.pyansys.com/version/stable/) packages:

* [`ansys-fluent-core`](https://github.com/ansys/pyfluent)
* [`ansys-fluent-parametric`](https://github.com/ansys/pyfluent-parametric)
* [`ansys-fluent-visualization`](https://github.com/ansys/pyfluent-visualization)


## Installation

The installation is possible via `mamba` packages, using the command

```shell
mamba env create -f environment.yml
```


## Prepare the files

* **`case`**: put in this folder the case files (`.cas.h5`) generated before for the robot in the nominal configuration (file name = configuration name) and for $(\alpha=0^\circ;\beta=0^\circ)$
* **`data/outputParameters`**: setup the file such that the first line contains in order the input parameters name followed by the report definition names to be computed as simulation output
* **`src`**: insert the configurations to be tested in the `jointConfig.csv` file following the file formatting, then also the pitch and yaw angles in `pitchAngles.csv`, `yawAngles.csv` and `yawAnglesStart.csv` (this last one is only valid for the first simulation cycle, in case the previous process failed before finishing the simulations for a configuration)


## How to run the code

Run **`src/runMesh.py`** python script inside the environment created using `mamba` packages.
Have fun!


# Extras

## `tmux` cheatsheet 

Reminder of some `tmux` simple commands to manage remote sessions on ws/srv:

```python 
tmux new -s fluent_0                        # create a new session named fluent_0
tmux detach                                 # exit session
tmux new -s fluent_1                        # create a new session named fluent_1
tmux attach -t fluent_0                     # enter first session (fluent_0)
tmux switch -t fluent_1                     # switch from current session to another (fluent_1)
tmux ls                                     # list open sessions
tmux rename-session -t fluent_0 fluent_9    # rename session (fluent_0->fluent_9)
tmux kill-session -t fluent_1               # kill session (fluent_1)
```

