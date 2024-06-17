"""
Author: Antonello Paolino
Date: 2024-05-29
Description:    This code uses the iDynTree package to retrieve the robot status,
                then it generates a 2D representation fo the 3D pressure map on
                the robot component surfaces
"""

# Import libraries
import numpy as np
import pathlib
import glob
import re
# Import custom classes
from robot import Robot
from flow import FlowImporter

def main():
    # Initialize robot and flow objects
    robot_name = "iRonCub-Mk3"
    robot = Robot(robot_name)
    
    # Dataset directory
    data_dir = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[-3:] / "database-extended"
    
    # Images directory
    img_dir = pathlib.Path(__file__).parents[1] / "images"
    
    # Get the files list (just the names)
    file_names = [pathlib.Path(file).name for file in glob.glob(str(data_dir / "*.dtbs"))]
    
    # Group the files by the joint configuration
    joint_configs = list(set([file_name.split("-")[0] for file_name in file_names]))

    # Load csv file
    joint_config_file_path = pathlib.Path(__file__).parents[4] / "meshing" / "src" / "jointConfigFull-mk3.csv"
    joint_configurations = np.genfromtxt(joint_config_file_path, delimiter=",", dtype=str)
    
    dataset = {}
    for joint_config_name in joint_configs:        
        # Get the joint positions
        joint_positions = joint_configurations[joint_configurations[:,0] == joint_config_name][0,1:].astype(float)
        # Get the pitch and yaw angles list
        pitch_yaw_angles = find_pitch_yaw_angles(joint_config_name, file_names)
        # Initialize lists
        images = []
        pitch_angles = []
        yaw_angles = []
        
        # Cycle on pitch and yaw angles
        progress_index = 0
        for pitch_angle, yaw_angle in pitch_yaw_angles:
            # Cast angles to integers
            pitch_angle = int(pitch_angle)
            yaw_angle = int(yaw_angle)
            # Set robot state
            robot.set_state(pitch_angle, yaw_angle, joint_positions)
            # Initialize flow object
            flow = FlowImporter(robot_name)
            # Compute link to world trasnformations
            link_H_world_dict = {}
            for surface_index in range(len(robot.surface_list)):
                # Compute the transformation from the link frame to the world frame (using zero rotation angles)
                surface_world_H_link = robot.compute_world_to_link_transform(frame_name=robot.surface_frames[surface_index], rotation_angle=0.0)
                surface_link_H_world = robot.invert_homogeneous_transform(surface_world_H_link) # alternative: np.linalg.inv(world_H_link)
                link_H_world_dict[robot.surface_list[surface_index]] = surface_link_H_world
            # Import fluent data from all surfaces
            flow.import_raw_fluent_data(joint_config_name, pitch_angle, yaw_angle, robot.surface_list)        
            flow.transform_local_fluent_data(link_H_world_dict, flow_velocity=17.0, flow_density=1.225)
            flow.assign_global_fluent_data()
            # Data Interpolation and Image Generation 
            resolution_scaling_factor = 1 # 1 for 1060 [px/m]
            surface_resolution = np.array(robot.image_resolutions)
            image_resolution_scaled = (surface_resolution * resolution_scaling_factor).astype(int) # scale to apply to the image resolution
            flow.interpolate_flow_data(image_resolution_scaled, robot.surface_list, robot.surface_axes)
            flow.assemble_images()
            
            # Non-dimensionalization
            # Cast image maximum value to 1
            maximum_indices = np.where(flow.image >= 1)
            flow.image[maximum_indices] = 1
            # Cast image minimum value to -5
            minimum_indices = np.where(flow.image <= -5)
            flow.image[minimum_indices] = -5
            # Non-dimensionalize the image between 0 and 1
            flow.image = (flow.image + 6) / 7
            # Change NaN values to 0
            nan_indices = np.where(np.isnan(flow.image))
            flow.image[nan_indices] = 0
            
            # Store data
            images.append(flow.image)
            pitch_angles.append(pitch_angle)
            yaw_angles.append(yaw_angle)
            
            progress_index += 1
            print(f"{joint_config_name} configuration progress: {progress_index}/{pitch_yaw_angles.shape[0]}", end='\r', flush=True)
            
        # Assign dataset variables
        dataset[joint_config_name] = {
            "pitch_angles": np.array(pitch_angles),
            "yaw_angles": np.array(yaw_angles),
            "images": np.array(images)
        }
        
        # Save dataset
        np.save(str(img_dir / f"{joint_config_name}-dataset.npy"), dataset[joint_config_name])
        print(f"{joint_config_name} configuration dataset saved. \n")
        
    # Save dataset
    np.save(str(img_dir / "dataset.npy"), dataset)
    print("Dataset saved.")
        


def find_pitch_yaw_angles(joint_config_name, file_names):
    segmented_files = [file_name.split("-") for file_name in file_names if file_name.split("-")[0] == joint_config_name]
    pitch_yaw_angles = np.empty((0,2))
    for file_name in segmented_files:
        index = 1
        if file_name[index] != "":
            pitch_angle = int(file_name[index])
            index += 1
        else:
            pitch_angle = -int(file_name[index+1])
            index += 2
        if file_name[index] != "":
            yaw_angle = int(file_name[index])
        else:
            yaw_angle = -int(file_name[index+1])
        pitch_yaw_angles = np.vstack((pitch_yaw_angles, [pitch_angle, yaw_angle]))
    # Remove duplicates
    pitch_yaw_angles = np.unique(pitch_yaw_angles, axis=0)
    return pitch_yaw_angles

if __name__ == "__main__":
    main()
