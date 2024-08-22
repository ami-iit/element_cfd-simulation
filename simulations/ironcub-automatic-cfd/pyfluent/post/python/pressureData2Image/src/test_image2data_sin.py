"""
Author: Antonello Paolino
Date: 2024-05-29
Description:    This code uses the iDynTree package to retrieve the robot status,
                then it generates 3D data of flow variables extracted from 2D images
"""

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pathlib
# Import custom classes
from robot import Robot
from flow import FlowGenerator, FlowVisualizer

def main():
    # Initialize robot and flow objects
    robot_name = "iRonCub-Mk3"
    robot = Robot(robot_name)
    flow = FlowGenerator(robot_name)

    # Define robot state parameters
    pitch_angle = 30
    yaw_angle = 0
    joint_config_name = "flight30"
    joint_positions = np.array([0,0,0,-30.7,12.9,26.5,58.3,-30.7,12.9,26.5,58.3,0,10,0,0,0,10,0,0])*np.pi/180
    
    # Set robot state
    robot.set_state(pitch_angle, yaw_angle, joint_positions)
    
    ###############################################################################################################
    ####################### HERE THERE SHOULD BE THE ALGORITHM TO GENERATE THE LOCAL IMAGES #######################
    ###############################################################################################################
    # Load image data
    joint_config_name_loading = "flight30"
    pitch_angle_loading = 30
    yaw_angle_loading = 0
    project_directory = pathlib.Path(__file__).parents[1]
    image_directory = project_directory / "images"
    assembled_image = np.load(image_directory / f"{joint_config_name_loading}-{pitch_angle_loading}-{yaw_angle_loading}-pressure.npy")
    # Separate the image into the 2D images of the surfaces
    flow.separate_images(assembled_image)
    ###############################################################################################################
    ###############################################################################################################
    
    # Mesh_robot for importing the pointcloud mesh
    robot_ref = Robot(robot_name)
    pitch_angle_ref = 30
    yaw_angle_ref = 0
    joint_config_name_ref = "flight30"
    joint_positions_ref = np.array([0,0,0,-30.7,12.9,26.5,58.3,-30.7,12.9,26.5,58.3,0,10,0,0,0,10,0,0])*np.pi/180
    robot_ref.set_state(pitch_angle_ref, yaw_angle_ref, joint_positions_ref)
    
    link_H_world_ref_dict = {}
    world_H_link_dict = {}
    for surface_index in range(len(robot.surface_list)):
        # Compute the transformation from the reference world frame to the link frame (using zero rotation angles)
        surface_world_H_link = robot_ref.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
        surface_link_H_world = robot_ref.invert_homogeneous_transform(surface_world_H_link) # alternative: np.linalg.inv(world_H_link)
        link_H_world_ref_dict[robot.surface_list[surface_index]] = surface_link_H_world
        # Compute the transformation from the link frame to the current world frame (using zero rotation angles)
        world_H_link_dict[robot.surface_list[surface_index]] = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
    
    flow.interpolate_sinusoid_data_from_image(robot.surface_list, robot.surface_axes, link_H_world_ref_dict, world_H_link_dict)
    
    ##############################################################################################
    ################################# Plots and 3D visualization #################################
    ##############################################################################################
    
    flowViz = FlowVisualizer(flow)
    
    # Enable LaTeX text rendering
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 24

    # Display the imported image
    fig1, ax1 = plt.subplots()
    plt.get_current_fig_manager().window.showMaximized()
    ax1.imshow(flow.image[0,:,:], origin='upper', cmap='jet', vmax=1, vmin=-1)
    ax1.axis("off")
    ax1.set_title("Assembled Image")
    cbar = fig1.colorbar(ax1.images[0], ax=ax1, orientation='vertical', fraction=0.02, pad=0.45)
    cbar.set_label(r'$\sin\theta$')
    
    # Display the 2D separated images
    fig2 = plt.figure("Separated Images")
    plt.get_current_fig_manager().window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax2 = fig2.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_im = ax2.imshow(flow.surface[surface_name].image[0,:,:], origin='lower', cmap='jet', vmax=1, vmin=-1)
        ax2.set_title(surface_name[8:])
        ax2.set_xlim([-10, flow.surface[surface_name].image.shape[2]+10])
        ax2.set_ylim([-10, flow.surface[surface_name].image.shape[1]+10])
    cbar_ax = fig2.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig2.colorbar(last_im, cax=cbar_ax)
    cbar.set_label(r'$\sin\theta$')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.4)
    
    fig3 = plt.figure("2D Reconstructed Sinusoid")
    plt.get_current_fig_manager().window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax3 = fig3.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_plot = ax3.scatter(
            flow.surface[surface_name].theta,
            flow.surface[surface_name].z,
            c=flow.surface[surface_name].pressure_coefficient,
            s=5, cmap="jet", vmax=1, vmin=-1
            )
        ax3.set_title(robot.surface_list[surface_index][8:])
        ax3.set_xlabel(r'$\theta r_{mean}$ [m]')
        ax3.set_ylabel(r'$z$ [m]')
        # ax3.axis("equal")
        ax3.set_xlim([np.min(flow.surface[surface_name].theta), np.max(flow.surface[surface_name].theta)])
        ax3.set_ylim([np.min(flow.surface[surface_name].z), np.max(flow.surface[surface_name].z)])
    cbar_ax = fig3.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig3.colorbar(last_plot, cax=cbar_ax)
    cbar.set_label(r'$\sin\theta$')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.8, hspace=0.6)
    
    fig3 = plt.figure("2D Reconstructed Sinusoid Relative Error")
    plt.get_current_fig_manager().window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax3 = fig3.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_plot = ax3.scatter(
            flow.surface[surface_name].theta,
            flow.surface[surface_name].z,
            c=np.abs(np.divide(flow.surface[surface_name].pressure_coefficient-np.sin(flow.surface[surface_name].theta),np.sin(flow.surface[surface_name].theta))),
            s=5, cmap="jet", vmax=0.05, vmin=0
            )
        ax3.set_title(robot.surface_list[surface_index][8:])
        ax3.set_xlabel(r'$\theta r_{mean}$ [m]')
        ax3.set_ylabel(r'$z$ [m]')
        # ax3.axis("equal")
        ax3.set_xlim([np.min(flow.surface[surface_name].theta), np.max(flow.surface[surface_name].theta)])
        ax3.set_ylim([np.min(flow.surface[surface_name].z), np.max(flow.surface[surface_name].z)])
    cbar_ax = fig3.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig3.colorbar(last_plot, cax=cbar_ax)
    cbar.set_label(r'$\Delta\sin\theta$')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.8, hspace=0.6)
    
    fig4, (ax4, ax5) = plt.subplots(1, 2)
    plt.get_current_fig_manager().window.showMaximized()
    error = np.empty_like(flow.surface["ironcub_head"].pressure_coefficient)
    # plt.hist(data, bins=20, range=(0, 1), edgecolor='black')
    for surface_index, surface_name in enumerate(robot.surface_list):
        error = np.append(error, np.abs(np.divide(flow.surface[surface_name].pressure_coefficient-np.sin(flow.surface[surface_name].theta),np.sin(flow.surface[surface_name].theta))))
    ax4.hist(error, bins=20, range=(0, 1.0), edgecolor='black')
    ax4.set_title('Relative reconstruction error histogram')
    ax4.set_xlabel('Relative reconstruction error')
    ax4.set_ylabel('Number of gridpoints')
    ax4.yaxis.grid()
    ax5.hist(error, bins=20, range=(0, 1.0), edgecolor='black')
    ax5.set_title('Relative reconstruction error histogram (zoom)')
    ax5.set_xlabel('Relative reconstruction error')
    ax5.set_ylabel('Number of gridpoints')
    ax5.set_ylim([0, 100])
    ax5.yaxis.grid()
    
    plt.show(block=False)
    
    # Display the 3D pressure pointcloud error
    # flowViz.plot_surface_pointcloud(flow_variable=abs(flow.cp-flow.fx), robot_meshes=robot.load_mesh())
    
    input("Press Enter to close the figures...")


if __name__ == "__main__":
    main()
