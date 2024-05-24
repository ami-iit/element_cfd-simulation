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

from robot import Robot
from flow import Flow

def main():
    # Set robot
    robot_name = "iRonCub-Mk3"
    robot = Robot(robot_name)
    flow = Flow(robot_name)

    # Define robot state parameters (TODO: get them from outputParameters)
    pitch_angle = 90
    yaw_angle = 0
    joint_config_name = "hovering"
    joint_positions = np.array([0,0,0,0,16.6,40,15,0,16.6,40,15,0,10,7,0,0,0,0,10,7,0,0,0])*np.pi/180 # 0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,0.0,0.0,10.0,7.0,0.0,0.0,0.0
    # joiint_config_name = "hovering2"
    # joint_positions = np.array([0,0,0,0,21.6,40,15,0,21.6,40,15,0,10,7,0,0,0,0,10,7,0,0,0])*np.pi/180 # 0.0,0.0,0.0,-10.0,25.0,40.0,15.0,-10.0,25.0,40.0,15.0,0.0,10.0,7.0,0.0,0.0,0.0,0.0,10.0,7.0,0.0,0.0,0.0

    # Set robot state
    robot.set_state(pitch_angle, yaw_angle, joint_positions)
    # Visualize robot config
    # robot.visualize()
    
    
    for surface_index in range(len(robot.surface_list)):

        # Compute the transformation from the link frame to the world frame (using zero rotation angles)
        world_H_link = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
        link_H_world = robot.invert_homogeneous_transform(world_H_link) # alternative: np.linalg.inv(world_H_link)

        flow.import_fluent_data(joint_config_name=joint_config_name, pitch_angle=pitch_angle, yaw_angle=yaw_angle, surface_name=robot.surface_list[surface_index])
        flow.transform_fluent_data(link_H_world, flow_velocity=17.0, flow_density=1.225)
        # flow.plot_surface_3D_map_local(flow.pressure_coefficient, mesh_path=str(robot.mesh_path / f"{robot.surface_meshes[surface_index]}.stl"))

        image_resolution = 800 # [px/m]
        mask_threshold = 0.02 # [m]

        # theta, z, X, Y, pressure_coefficient_interp = flow.interpolate_pressure_data(main_axis=robot.surface_axes[surface_index], resolution = image_resolution, mask_threshold = mask_threshold)
        # print(f"Surface {robot.surface_list[surface_index]} resolution: {pressure_coefficient_interp.shape}")
        
        # # Display the theta, z and CP data
        # plt.figure()
        # plt.subplot(1, 2, 1)
        # plt.scatter(theta, z, c=flow.pressure_coefficient, cmap='jet')
        # plt.colorbar()
        # plt.xlabel(r'$\theta r_{mean}$ [m]')
        # plt.ylabel(r'$z$ [m]')
        # plt.axis('equal')
        # plt.title('Simulation pressure map')

        # # Display the 2D image
        # plt.subplot(1, 2, 2)
        # plt.imshow(pressure_coefficient_interp, extent=(np.min(X), np.max(X), np.min(Y), np.max(Y)), origin='lower', cmap='jet')
        # plt.colorbar()
        # # plt.xlabel(r'$\theta r_{mean}$ [m]')
        # # plt.ylabel(r'$z$ [m]')
        # plt.axis('equal')
        # plt.title('Interpolated image')
    
    # plt.show(block=False)
    
    flow.plot_surface_point_cloud(flow_variable=flow.cp, meshes=robot.load_mesh())

    print("fermoooo")
    
    
    

if __name__ == "__main__":
    main()





