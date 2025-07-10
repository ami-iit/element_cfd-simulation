import os
import pathlib
import matplotlib.pyplot as plt

# Define test name manually if needed or ...
test_name = ""

# ... get the latest test name
test_dir = pathlib.Path(__file__).parents[1] / "bin" / "export"
if test_name.__len__() <= 4:
    test_list = os.listdir(test_dir)
    test_list.sort()

    if test_list:
        test_name = test_list[-1]
    else:
        print("No tests found in the directory.")

data_path = test_dir / test_name / "data" / "FP16C"

############################# Read the forces data #############################
with open(str(data_path / "forces.dat"), "r") as file:
    # Initialize empty lists for each column
    time, CdAs, ClAs, CsAs = [], [], [], []

    next(file)  # Skip the first line (assuming it contains headers)
    for line in file:
        # Split each line into columns
        columns = line.split()

        # Store the values in their respective lists
        time.append(float(columns[1]))
        CdAs.append(float(columns[2]))
        ClAs.append(float(columns[3]))
        CsAs.append(float(columns[4]))

# Get the average values of the forces
CdA_steady, ClA_steady, CsA_steady = [], [], []

for i in range(len(time)):
    if time[i] >= 0.8 * max(time):
        CdA_steady.append(CdAs[i])
        ClA_steady.append(ClAs[i])
        CsA_steady.append(CsAs[i])

CdA_avg = sum(CdA_steady) / len(CdA_steady)
ClA_avg = sum(ClA_steady) / len(ClA_steady)
CsA_avg = sum(CsA_steady) / len(CsA_steady)


############################# Read the torques data #############################
with open(str(data_path / "torques.dat"), "r") as file:
    # Initialize empty lists for each column
    time, CrAls, CpAls, CyAls = [], [], [], []

    next(file)  # Skip the first line (assuming it contains headers)
    for line in file:
        # Split each line into columns
        columns = line.split()

        # Store the values in their respective lists
        time.append(float(columns[1]))
        CrAls.append(float(columns[2]))
        CpAls.append(float(columns[3]))
        CyAls.append(float(columns[4]))

# Get the average values of the torques
CrAl_steady, CpAl_steady, CyAl_steady = [], [], []

for i in range(len(time)):
    if time[i] >= 0.8 * max(time):
        CrAl_steady.append(CrAls[i])
        CpAl_steady.append(CpAls[i])
        CyAl_steady.append(CyAls[i])

CrAl_avg = sum(CrAl_steady) / len(CrAl_steady)
CpAl_avg = sum(CpAl_steady) / len(CpAl_steady)
CyAl_avg = sum(CyAl_steady) / len(CyAl_steady)

############################# Plot the data #############################
fig1 = plt.figure(figsize=(16, 4))
xlimits = [0, max(time)]

# CdA plot
ax1 = fig1.add_subplot(131)
ax1.plot(time, CdAs, label="unsteady", color="black")
ax1.plot(
    time,
    [CdA_avg] * len(time),
    label=r"$(C_DA)_{avg}=$" + "{:.3f}".format(CdA_avg),
    color="red",
)

ax1.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax1.set_xlabel(r"$t$ [s]")
ax1.xaxis.label.set_fontsize(12)
ax1.set_xlim(xlimits)

ax1.yaxis.set_label_coords(-0.15, 0.5)  # Adjust the y-axis label position
ax1.yaxis.label.set_fontsize(12)
ax1.yaxis.set_tick_params()
ax1.set_ylim([0, 1])

ax1.set_title(r"$C_DA$")
ax1.grid()
ax1.legend()

# ClA plot
ax2 = fig1.add_subplot(132)
ax2.plot(time, ClAs, label="unsteady", color="black")
ax2.plot(
    time,
    [ClA_avg] * len(time),
    label=r"$(C_LA)_{avg}=$" + "{:.4f}".format(ClA_avg),
    color="red",
)

ax2.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax2.set_xlabel(r"$t$ [s]")
ax2.xaxis.label.set_fontsize(12)
ax2.set_xlim(xlimits)

ax2.yaxis.set_label_coords(-0.10, 0.5)  # Adjust the y-axis label position
ax2.yaxis.label.set_fontsize(12)
ax2.yaxis.set_tick_params()
ax2.set_ylim([-0.1, 0.1])

ax2.set_title(r"$C_LA$")
ax2.grid()
ax2.legend()

# CsA plot
ax3 = fig1.add_subplot(133)
ax3.plot(time, CsAs, label="unsteady", color="black")
ax3.plot(
    time,
    [CsA_avg] * len(time),
    label=r"$(C_SA)_{avg}=$" + "{:.4f}".format(CsA_avg),
    color="red",
)

ax3.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax3.set_xlabel(r"$t$ [s]")
ax3.xaxis.label.set_fontsize(12)
ax3.set_xlim(xlimits)

ax3.yaxis.set_label_coords(-0.05, 0.5)  # Adjust the y-axis label position
ax3.yaxis.label.set_fontsize(12)
ax3.yaxis.set_tick_params()

ax3.set_title(r"$C_SA$")
ax3.grid()
ax3.legend()

########################## Moments plots ##########################
fig2 = plt.figure(figsize=(16, 4))

# CrAl plot
ax1 = fig2.add_subplot(131)
ax1.plot(time, CrAls, label="unsteady", color="black")
ax1.plot(
    time,
    [CrAl_avg] * len(time),
    label=r"$(C_rAl)_{avg}=$" + "{:.4f}".format(CrAl_avg),
    color="red",
)

ax1.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax1.set_xlabel(r"$t$ [s]")
ax1.xaxis.label.set_fontsize(12)
ax1.set_xlim(xlimits)

ax1.yaxis.set_label_coords(-0.15, 0.5)  # Adjust the y-axis label position
ax1.yaxis.label.set_fontsize(12)
ax1.yaxis.set_tick_params()
ax1.set_ylim([-0.01, 0.01])

ax1.set_title(r"$C_rAl$")
ax1.grid()
ax1.legend()

# CpAl plot
ax2 = fig2.add_subplot(132)
ax2.plot(time, CpAls, label="unsteady", color="black")
ax2.plot(
    time,
    [CpAl_avg] * len(time),
    label=r"$(C_pAl)_{avg}=$" + "{:.4f}".format(CpAl_avg),
    color="red",
)

ax2.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax2.set_xlabel(r"$t$ [s]")
ax2.xaxis.label.set_fontsize(12)
ax2.set_xlim(xlimits)

ax2.yaxis.set_label_coords(-0.10, 0.5)  # Adjust the y-axis label position
ax2.yaxis.label.set_fontsize(12)
ax2.yaxis.set_tick_params()
ax2.set_ylim([-0.1, 0.1])

ax2.set_title(r"$C_pAl$")
ax2.grid()
ax2.legend()

# CyAl plot
ax3 = fig2.add_subplot(133)
ax3.plot(time, CyAls, label="unsteady", color="black")
ax3.plot(
    time,
    [CyAl_avg] * len(time),
    label=r"$(C_yAl)_{avg}=$" + "{:.4f}".format(CyAl_avg),
    color="red",
)

ax3.xaxis.set_label_coords(0.5, -0.08)  # Adjust the x-axis label position
ax3.set_xlabel(r"$t$ [s]")
ax3.xaxis.label.set_fontsize(12)
ax3.set_xlim(xlimits)

ax3.yaxis.set_label_coords(-0.05, 0.5)  # Adjust the y-axis label position
ax3.yaxis.label.set_fontsize(12)
ax3.yaxis.set_tick_params()
ax3.set_ylim([-0.01, 0.01])

ax3.set_title(r"$C_yAl$")
ax3.grid()
ax3.legend()


# Showing the plots
plt.show(block=False)

# Closing all the plots
wait = input("Press Enter to close and save the figures.")

# Saving figures
fig_path = pathlib.Path(__file__).parents[0] / "forces" / test_name
fig1.savefig(str(fig_path) + "_forces.png")
fig2.savefig(str(fig_path) + "_torques.png")


print(f"Figures successfully saved as '{fig_path}'.")
