## Wind tunnel setup CFD results

in this repo there are the aerodynamic force and torque coefficients results for the CFD simulations on the iRonCub wind tunnel setup geometry according to different _Meshes_, _Configurations_ and _Turbulence models_.
the files are stored in _Fluent_ `.out` and standard `.txt` formats.

### Mesh

* **953C:** _Full Mesh_ with original sizings used to compare and evaluate wind tunnel experiments results $(\approx 9.53\times 10^6\ cells)$
* **202C:** mesh with first step sizings reduction $(\approx 2.02\times 10^6\ cells)$
* **050C:** mesh with second step sizings reduction $(\approx 0.50\times 10^6\ cells)$
* **024C:** mesh with third step sizings reduction $(\approx 0.24\times 10^6\ cells)$
* **011C:** mesh with last step sizings reduction $(\approx 0.11\times 10^6\ cells)$

### Robot configuration

* `hovering`
* `flight30`
* `flight50`
* `flight60`
* `hovJointVar5`
* `hovJointVar9`

### RANS turbulence model

* _Realizable_ $k-\varepsilon$
* _SST_ $k-\omega$