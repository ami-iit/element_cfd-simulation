"""
Author: Antonello Paolino
Date: 2024-05-29
Description:    This code uses the iDynTree package to retrieve the robot status,
                then it generates 3D data of flow variables extracted from 2D images
"""

# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import numpy as np
import matplotlib.pyplot as plt
import pathlib

from robot import Robot
from flow import FlowGenerator

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
    project_directory = pathlib.Path(__file__).parents[1]
    image_directory = project_directory / "images"
    assembled_image = np.load(image_directory / f"{joint_config_name}-{pitch_angle}-{yaw_angle}-pressure.npy")
    # Display the loaded image as vertically flipped
    fig1 = plt.figure("Assembled Image")
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.imshow(assembled_image, origin='upper', cmap='jet', vmax=1, vmin=-2)
    ax1.axis("off")
    plt.show(block=False)
    # Separate the image into the 2D images of the surfaces
    images = flow.separate_images(assembled_image)
    # Display the 2D image without borders, with fixed axes limits and aspect ratio
    fig2 = plt.figure("Interpolated Images")
    ax_counter = 1
    for surface_name, image in images.items():
        ax2 = fig2.add_subplot(4, 6, ax_counter)
        ax2.imshow(image, origin='lower', cmap='jet', vmax=1, vmin=-2)
        ax2.set_title(surface_name)
        ax2.set_xlim([-10, 660])
        ax2.set_ylim([-10, 300])
        ax_counter += 1
    plt.show(block=False)
    ###############################################################################################################
    ###############################################################################################################
    
    fig3 = plt.figure("2D Pressure Map")
    
    for surface_index in range(len(robot.surface_list)):

        # Compute the transformation from the link frame to the world frame (using zero rotation angles)
        world_H_link = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
        link_H_world = robot.invert_homogeneous_transform(world_H_link) # alternative: np.linalg.inv(world_H_link)

        # flow.import_fluent_data(joint_config_name=joint_config_name, pitch_angle=pitch_angle, yaw_angle=yaw_angle, surface_name=robot.surface_list[surface_index])
        # flow.transform_fluent_data(link_H_world, flow_velocity=17.0, flow_density=1.225)
        
        flow.get_surface_mesh_points(
            surface_name=robot.surface_list[surface_index],
            link_H_world=link_H_world,
            joint_config_name="flight30"
            )
        theta, z, pressure_coefficient_local = flow.interpolate_flow_data_2D(
            image=images[robot.surface_list[surface_index]],
            main_axis=robot.surface_axes[surface_index],
            surface_name=robot.surface_list[surface_index]
            )
        
        # Display the theta, z and CP data in the fig1
        ax3 = fig3.add_subplot(4, 6, surface_index+1)
        ax3.scatter(theta, z, c=flow.pressure_coefficient, cmap="jet")
        ax3.set_title(robot.surface_list[surface_index][8:])
        ax3.set_xlabel(r'$\theta r_{mean}$ [m]')
        ax3.set_ylabel(r'$z$ [m]')
        ax3.axis("equal")
        ax3.set_xlim([np.min(theta), np.max(theta)])
        ax3.set_ylim([np.min(z), np.max(z)])       
        # TODO: colorbar
    
    plt.show(block=False)
    
    # Display the 3D pressure pointcloud
    flow.plot_surface_pointcloud(flow_variable=flow.cp, meshes=robot.load_mesh())


if __name__ == "__main__":
    main()
