# pyfluent

## Intro

This repo contains all the code to run automatic CFD simulation on iRonCub-Mk1 and iRonCub-Mk3 geometries using the _pyfluent API_ for _Python_. The project is divided into:

* **`auto-cfd-geom`**: the code here allows to generate geometries in _ANSYS Workbench_ starting from a given robot joint configurations file. The generated geometries can then be passed to the next cycle of the automatic process.

* **`auto-cfd-mesh-py`**: here the code using the `pyfluent meshing API` is implemented generating a mesh on the iRonCub geometry and returning a `.cas` case file with all the required settings to perform aotomatic CFD simulations changing the attitude of the robot.

* **`auto-cfd-sim-py`**: this repo encloses all the necessary files to perform automatic cfd simulations starting from already defined case files and pitch and yaw angles input files, the process uses the new `pyfluent` packages which allow to use Fluent directly from command within a fully-integrated python code. This routine has 2 main advantages: 
  - `Native GPU Solver` available from `ANSYS Fluent` (not from `ANSYS Workbench`);
  - Easy to adapt to run on external workstations/servers after importing all the correct packages/files (or cloning the repo). 


## Installation

The installation is possible via `mamba` packages, using the command

```shell
mamba env create -f environment.yml
```

## Extras

### `tmux` cheatsheet 

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

