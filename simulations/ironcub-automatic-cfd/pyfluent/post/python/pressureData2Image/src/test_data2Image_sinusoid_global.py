"""
Author: Antonello Paolino
Date: 2024-05-15
Description:    This code uses the iDynTree package to retrieve the robot status,
                then it generates a 2D representation fo the 3D pressure map on
                the robot component surfaces
"""

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pathlib
# Import custom classes
from robot import Robot
from flow import FlowImporter, FlowVisualizer

def main():
    # Initialize robot and flow objects
    robot_name = "iRonCub-Mk3"
    robot = Robot(robot_name)
    flow = FlowImporter(robot_name)

    # Define robot state parameters (TODO: get them from outputParameters)
    pitch_angle = 30
    yaw_angle = 0
    joint_config_name = "flight30"
    joint_positions = np.array([0,0,0,-30.7,12.9,26.5,58.3,-30.7,12.9,26.5,58.3,0,10,0,0,0,10,0,0])*np.pi/180

    # Set robot state
    robot.set_state(pitch_angle, yaw_angle, joint_positions)
    
    link_H_world_dict = {}
    for surface_index in range(len(robot.surface_list)):
        # Compute the transformation from the link frame to the world frame (using zero rotation angles)
        surface_world_H_link = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
        surface_link_H_world = robot.invert_homogeneous_transform(surface_world_H_link) # alternative: np.linalg.inv(world_H_link)
        link_H_world_dict[robot.surface_list[surface_index]] = surface_link_H_world
    
    # Import fluent data from all surfaces
    print(f"Importing and transforming data ...")
    flow.import_raw_fluent_data(joint_config_name, pitch_angle, yaw_angle, robot.surface_list)
    flow.transform_local_fluent_data(link_H_world_dict, flow_velocity=17.0, flow_density=1.225)
    flow.assign_global_fluent_data()
    
    # Data Interpolation and Image Generation 
    resolution_scaling_factor = 1 # 1 for 1060 [px/m]
    surface_resolution = np.array(robot.image_resolutions)
    image_resolution_scaled = (surface_resolution * resolution_scaling_factor).astype(int) # scale to apply to the image resolution
    
    print("Interpolating and generating images ...")
    field_direction = "z"
    flow.interpolate_global_sinusoid_flow_data(field_direction, image_resolution_scaled, robot.surface_list, robot.surface_axes)
    flow.assemble_images()
    
    print("Saving image ...")
    project_directory = pathlib.Path(__file__).parents[1]
    image_directory = project_directory / "images"
    np.save(str(image_directory/f"{joint_config_name}-{pitch_angle}-{yaw_angle}-pressure.npy"), flow.image)

    ##############################################################################################
    ################################# Plots and 3D visualization #################################
    ##############################################################################################
    
    flowViz = FlowVisualizer(flow)
    flowViz.plot_surface_pointcloud(flow_variable=flow.cp, robot_meshes=robot.load_mesh())
    
    # Enable LaTeX text rendering
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 24
    
    cbar_label = r'$\sin (^{G[I]}' + field_direction + r')$'
    
    fig3 = plt.figure("2D sinusoid data")
    plt.get_current_fig_manager().window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax3 = fig3.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_plot = ax3.scatter(
            flow.surface[surface_name].theta,
            flow.surface[surface_name].z,
            c=flow.surface[surface_name].field_function,
            s=5, cmap="jet", vmax=1, vmin=-1
            )
        ax3.set_title(robot.surface_list[surface_index][8:])
        ax3.set_xlabel(r'$\theta$ [rad]')
        ax3.set_ylabel(r'$z$ [m]')
        # ax3.axis("equal")
        ax3.set_xlim([np.min(flow.surface[surface_name].theta), np.max(flow.surface[surface_name].theta)])
        ax3.set_ylim([np.min(flow.surface[surface_name].z), np.max(flow.surface[surface_name].z)])
    cbar_ax = fig3.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig3.colorbar(last_plot, cax=cbar_ax)
    cbar.set_label(cbar_label)
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.8, hspace=0.6)
    
    fig4 = plt.figure("Interpolated Images")
    plt.get_current_fig_manager().window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax4 = fig4.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_im = ax4.imshow(flow.surface[surface_name].image[0,:,:], origin='lower', cmap='jet', vmax=1, vmin=-1)
        ax4.set_title(surface_name[8:])
        ax4.set_xlim([-10, image_resolution_scaled[surface_index,1]+10])
        ax4.set_ylim([-10, image_resolution_scaled[surface_index,0]+10])
    cbar_ax = fig4.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig4.colorbar(last_im, cax=cbar_ax)
    cbar.set_label(cbar_label)
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.4)
    
    # Display the assembled image as vertically flipped
    fig5, ax5 = plt.subplots()
    plt.get_current_fig_manager().window.showMaximized()
    ax5.imshow(flow.image[0,:,:], origin='upper', cmap='jet', vmax=np.max(flow.image[0,:,:]), vmin=np.min(flow.image[0,:,:]))
    ax5.axis("off")
    ax5.set_title("Assembled Image")
    cbar = fig5.colorbar(ax5.images[0], ax=ax5)
    cbar.set_label(cbar_label)
    
    plt.show(block=False)
    
    input("Press Enter to close all figures and exit ...")
    

if __name__ == "__main__":
    main()
