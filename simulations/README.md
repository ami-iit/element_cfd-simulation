## `simulations`

In this repo some of the simulation projects and files used for the CFD studies are stored:

* **`sphere`**: contains some of the early-stage simulations files which have been perfromed to assess the accuracy of CFD simulations on massively separated airflows around bluff object, comparing them with experimental results;

* **`ironcub-automatic-cfd`**: after reducing the simulations computational cost, preserving the numerical results accuracy and validity, the CFD simulations have been included in a full pipeline modifying the robot geometry in _ANSYS SpaceClaim_, generating the computational mesh and solving the airflow field with _ANSYS Fluent_;

* **`lattice-boltzmann-method`**: here there are the execution files for simulating iRonCub robot using the software `FluidX3D` which employs Lattice-Boltzmann Method equations for fluid dynamic simulations, differently as done previously with the Finite Volume Method software `ANSYS Fluent`.