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
from flow import FlowImporter

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
    # joint_config_name = "hovering"
    # joint_positions = np.array([0,0,0,0,16.6,40,15,0,16.6,40,15,0,10,7,0,0,10,7,0])*np.pi/180
    # joint_config_name = "hovering2"
    # joint_positions = np.array([0,0,0,0,21.6,40,15,0,21.6,40,15,0,10,7,0,0,0,0,10,7,0,0,0])*np.pi/180

    # Set robot state
    robot.set_state(pitch_angle, yaw_angle, joint_positions)
    # Visualize robot config
    # robot.visualize()
    
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
    
    # visualize and check data
    test_surface_name = robot.surface_list[0]
    # flow.plot_local_pointcloud(flow.surface[test_surface_name])
    
    # Data Interpolation and Image Generation 
    resolution_scaling_factor = 1 # 1 for 1060 [px/m]
    
    surface_resolution = np.array(robot.image_resolutions)
    image_resolution_scaled = (surface_resolution * resolution_scaling_factor).astype(int) # scale to apply to the image resolution
    
    print("Interpolating and generating images ...")
    flow.interpolate_flow_data(image_resolution_scaled, robot.surface_list, robot.surface_axes)
    flow.assemble_images()
    
    print("Saving image ...")
    project_directory = pathlib.Path(__file__).parents[1]
    image_directory = project_directory / "images"
    np.save(str(image_directory/f"{joint_config_name}-{pitch_angle}-{yaw_angle}-pressure.npy"), flow.image)

    ##############################################################################################
    ################################# Plots and 3D visualization #################################
    ##############################################################################################
    
    # 3D visualization of the pressure map
    # flow.plot_surface_pointcloud(flow_variable=flow.cp, robot_meshes=robot.load_mesh())
    # flow.plot_surface_contour(flow_variable=flow.cp, robot_meshes=robot.load_mesh())
    
    # Enable LaTeX text rendering
    plt.rcParams['text.usetex'] = True
    
    fig2 = plt.figure("Head Interpolated Image")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    ax2 = fig2.add_subplot(1, 1, 1)
    ax2.imshow(flow.surface["ironcub_head"].image, origin='lower', cmap='jet', vmax=1, vmin=-2)
    ax2.set_xlim([-10, flow.surface["ironcub_head"].image.shape[1]+10])
    ax2.set_ylim([-10, flow.surface["ironcub_head"].image.shape[0]+10])
    cbar = fig2.colorbar(fig2.axes[0].images[0], ax=ax2, orientation='vertical')
    cbar.set_label(r'$C_p$')
    plt.show(block=False)
    
    
    fig1 = plt.figure("2D Pressure Map")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    last_plot = None
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax1 = fig1.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_plot = ax1.scatter(
            flow.surface[surface_name].theta,
            flow.surface[surface_name].z,
            c=flow.surface[surface_name].pressure_coefficient,
            s=1, cmap="jet", vmax=1, vmin=-2
            )
        ax1.set_title(robot.surface_list[surface_index][8:])
        ax1.set_xlabel(r'$\theta r_{mean}$ [m]')
        ax1.set_ylabel(r'$z$ [m]')
        ax1.axis("equal")
        ax1.set_xlim([np.min(flow.surface[surface_name].theta), np.max(flow.surface[surface_name].theta)])
        ax1.set_ylim([np.min(flow.surface[surface_name].z), np.max(flow.surface[surface_name].z)])
    cbar_ax = fig1.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig1.colorbar(last_plot, cax=cbar_ax)
    cbar.set_label(r'C_p')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.8, hspace=0.6)
    
    fig2 = plt.figure("Interpolated Images")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    gs = gridspec.GridSpec(4, 7, figure=1, width_ratios=[1, 1, 1, 1, 1, 1, 0.1])  # The last column is for the colorbar
    last_im = None
    for surface_index, surface_name in enumerate(robot.surface_list):
        ax2 = fig2.add_subplot(gs[surface_index // 6, surface_index % 6])
        last_im = ax2.imshow(flow.surface[surface_name].image, origin='lower', cmap='jet', vmax=1, vmin=-2)
        ax2.set_title(surface_name[8:])
        ax2.set_xlim([-10, image_resolution_scaled[surface_index,1]+10])
        ax2.set_ylim([-10, image_resolution_scaled[surface_index,0]+10])
    cbar_ax = fig2.add_subplot(gs[:, -1])  # Span all rows in the last column
    cbar = fig2.colorbar(last_im, cax=cbar_ax)
    cbar.set_label(r'C_p')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.4)
    
    # Display the assembled image as vertically flipped
    fig3 = plt.figure("Assembled Image")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    ax3 = fig3.add_subplot(1, 1, 1)
    image = ax3.imshow(flow.image, origin='upper', cmap='jet', vmax=1, vmin=-2)
    ax3.axis("off")
    fig3.colorbar(image, ax=ax3, orientation='vertical', fraction=0.02, pad=0.45)
    
    plt.show(block=False)
    
    print("stop")
    

if __name__ == "__main__":
    main()
