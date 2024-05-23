# Lattice Boltzmann Method

This is a different methodology to solve fluid flow fields, different to Finite Volume Method as implemented in the commercial software [`ANSYS Fluent`](https://www.ansys.com/products/fluids/ansys-fluent).
In this directory all the necessary files to simulate iRonCub whole-body geometry using the open-source code [`FluidX3D`](https://github.com/ProjectPhysX/FluidX3D) based on LBM is reported, plus some useful features in the `ironcub-mk1/utility` directory, useful to generate force and torque plots and cool videos from real-time rendered snapshots of the simulation.

## Installation

Through the `environment.yml` is possible to download the necessary `conda` packages for the utility directory python code, it is just necessary to run the following command in the shell (Linux OS) or in the command prompt (Windows OS):

```shell
mamba env create -f environment.yml
```

To execute the code it's necessary to move the directories in the [`FluidX3D`](https://github.com/ProjectPhysX/FluidX3D) cloned main repo!

Have fun!