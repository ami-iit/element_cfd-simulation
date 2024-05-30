"""
Author: Antonello Paolino
Date: 2024-05-15
Description:    This code uses the iDynTree package to retrieve the robot status,
                then it generates a 2D representation fo the 3D pressure map on
                the robot component surfaces
"""

# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import numpy as np
import matplotlib.pyplot as plt
import pathlib

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
    # joint_positions = np.array([0,0,0,0,16.6,40,15,0,16.6,40,15,0,10,7,0,0,0,0,10,7,0,0,0])*np.pi/180
    # joint_config_name = "hovering2"
    # joint_positions = np.array([0,0,0,0,21.6,40,15,0,21.6,40,15,0,10,7,0,0,0,0,10,7,0,0,0])*np.pi/180

    # Set robot state
    robot.set_state(pitch_angle, yaw_angle, joint_positions)
    # Visualize robot config
    # robot.visualize()
    
    fig1 = plt.figure("2D Pressure Map")
    fig2 = plt.figure("Interpolated Images")
    
    for surface_index in range(len(robot.surface_list)):

        # Compute the transformation from the link frame to the world frame (using zero rotation angles)
        world_H_link = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
        link_H_world = robot.invert_homogeneous_transform(world_H_link) # alternative: np.linalg.inv(world_H_link)

        flow.import_fluent_data(joint_config_name=joint_config_name, pitch_angle=pitch_angle, yaw_angle=yaw_angle, surface_name=robot.surface_list[surface_index])
        flow.transform_fluent_data(link_H_world, flow_velocity=17.0, flow_density=1.225)
        # flow.plot_surface_3D_map_local(flow.pressure_coefficient, mesh_path=str(robot.mesh_path / f"{robot.surface_meshes[surface_index]}.stl"))

        image_resolution = 800 # [px/m]
        surface_resolution = np.array(robot.image_resolutions[surface_index])
        image_resolution_scaled = surface_resolution * image_resolution/800 # scale to apply to the image resolution
        image_resolution_scaled = image_resolution_scaled.astype(int)
        
        theta, z, X, Y, pressure_coefficient_interp = flow.interpolate_flow_data(
            flow_variable = flow.pressure_coefficient,
            main_axis = robot.surface_axes[surface_index],
            resolution = image_resolution_scaled,
            surface_name = robot.surface_list[surface_index]
            )
        print(f"Surface {robot.surface_list[surface_index]} resolution: {pressure_coefficient_interp.shape}")
        
        # Display the theta, z and CP data in the fig1
        ax1 = fig1.add_subplot(4, 6, surface_index+1)
        ax1.scatter(theta, z, c=flow.pressure_coefficient, cmap="jet")
        ax1.set_title(robot.surface_list[surface_index][8:])
        ax1.set_xlabel(r'$\theta r_{mean}$ [m]')
        ax1.set_ylabel(r'$z$ [m]')
        ax1.axis("equal")
        ax1.set_xlim([np.min(theta), np.max(theta)])
        ax1.set_ylim([np.min(z), np.max(z)])       
        # TODO: colorbar
        
        # Display the 2D image without borders, with fixed axes limits and aspect ratio
        ax2 = fig2.add_subplot(4, 6, surface_index+1)
        ax2.imshow(pressure_coefficient_interp, origin='lower', cmap='jet', vmax=1, vmin=-2)
        ax2.set_title(robot.surface_list[surface_index][8:])
        # ax2.axis("off")
        ax2.set_xlim([-10, 660])
        ax2.set_ylim([-10, 300])
        # ax2.axis("equal")
        # TODO: colorbar
    
    plt.show(block=False)
    
    # Display the 3D pressure map
    flow.plot_surface_point_cloud(flow_variable=flow.cp, meshes=robot.load_mesh())
    
    image = flow.assemble_images()
    
    # Display the assembled image as vertically flipped
    fig3 = plt.figure("Assembled Image")
    ax3 = fig3.add_subplot(1, 1, 1)
    ax3.imshow(image, origin='upper', cmap='jet', vmax=1, vmin=-2)
    ax3.axis("off")
    plt.show(block=False)
    
    # Save assembled image as npy array
    project_directory = pathlib.Path(__file__).parents[1]
    image_directory = project_directory / "images"
    np.save(str(image_directory/f"{joint_config_name}-{pitch_angle}-{yaw_angle}-pressure.npy"), image)


if __name__ == "__main__":
    main()
