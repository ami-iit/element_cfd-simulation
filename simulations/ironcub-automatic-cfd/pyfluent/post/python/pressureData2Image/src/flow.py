import pathlib
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.interpolate import griddata
from scipy.spatial.transform import Rotation as R
from dataclasses import dataclass, field

@dataclass 
class SurfaceData:
    x_global: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    y_global: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    z_global: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    x_local: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    y_local: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    z_local: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    theta: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    z: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    pressure: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    x_shear_stress: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    y_shear_stress: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    z_shear_stress: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    pressure_coefficient: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    x_friction_coefficient: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    y_friction_coefficient: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    z_friction_coefficient: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    image: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,0)))
    
class FlowImporter:
    def __init__(self, robot_name):
        self.database_path = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[8:] / "database-extended"
        self.surface = {}
        self.x = np.empty(shape=(0,))
        self.y = np.empty(shape=(0,))
        self.z = np.empty(shape=(0,))
        self.cp = np.empty(shape=(0,))
        self.fx = np.empty(shape=(0,))
        self.fy = np.empty(shape=(0,))
        self.fz = np.empty(shape=(0,))
        self.image = np.empty(shape=(0,0))
    
    def import_raw_fluent_data(self, joint_config_name, pitch_angle, yaw_angle, surface_list):
        for surface_name in surface_list:
            database_file_path = str(self.database_path / f"{joint_config_name}-{pitch_angle}-{yaw_angle}-{surface_name}.dtbs")
            data = np.loadtxt(database_file_path, skiprows=1)
            # Assign the data to the surface object
            surface_data = SurfaceData()
            surface_data.x_global = data[:,1]
            surface_data.y_global = data[:,2]
            surface_data.z_global = data[:,3]
            surface_data.pressure = data[:,4]
            surface_data.x_shear_stress = data[:,5]
            surface_data.y_shear_stress = data[:,6]
            surface_data.z_shear_stress = data[:,7]
            self.surface[surface_name] = surface_data
        return
    
    def transform_local_fluent_data(self, link_H_world_dict, flow_velocity, flow_density):
        for surface_name, surface_data in self.surface.items():
            link_H_world = link_H_world_dict[surface_name]
            ones = np.ones((len(surface_data.x_global),))
            global_coordinates = np.vstack((surface_data.x_global,surface_data.y_global,surface_data.z_global,ones)).T
            local_coordinates = np.dot(link_H_world,global_coordinates.T).T
            self.surface[surface_name].x_local = local_coordinates[:,0]
            self.surface[surface_name].y_local = local_coordinates[:,1]
            self.surface[surface_name].z_local = local_coordinates[:,2]
            self.surface[surface_name].pressure_coefficient = surface_data.pressure/(0.5*flow_density*flow_velocity**2)
            self.surface[surface_name].x_friction_coefficient = surface_data.x_shear_stress/(0.5*flow_density*flow_velocity**2)
            self.surface[surface_name].y_friction_coefficient = surface_data.y_shear_stress/(0.5*flow_density*flow_velocity**2)
            self.surface[surface_name].z_friction_coefficient = surface_data.z_shear_stress/(0.5*flow_density*flow_velocity**2)
        return
    
    def assign_global_fluent_data(self):
        for surface_name, surface_data in self.surface.items():
            self.x = np.append(self.x, surface_data.x_global)
            self.y = np.append(self.y, surface_data.y_global)
            self.z = np.append(self.z, surface_data.z_global)
            self.cp = np.append(self.cp, surface_data.pressure_coefficient)
            self.fx = np.append(self.fx, surface_data.x_friction_coefficient)
            self.fy = np.append(self.fy, surface_data.y_friction_coefficient)
            self.fz = np.append(self.fz, surface_data.z_friction_coefficient)
        return 
    
    def plot_local_pointcloud(self, surface_data):
        points = np.vstack((surface_data.x_local,surface_data.y_local,surface_data.z_local)).T # 3D points
        # Normalize the colormap
        norm = plt.Normalize(vmin=-2, vmax=1)
        normalized_flow_variable = norm(surface_data.pressure_coefficient)
        colormap = cm.jet
        colors = colormap(normalized_flow_variable)[:,:3]
        # Create the point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)
        point_cloud.colors = o3d.utility.Vector3dVector(colors)
        # Create the local frame
        local_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
        # Add the geometries to the scene
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "local_frame", "geometry": local_frame},
        ]
        o3d.visualization.draw(geometries,show_skybox=False)
        return

    def interpolate_flow_data(self, image_resolution_list, surface_list, main_axes):
        for surface_index, surface_name in enumerate(surface_list):
            image_resolution = image_resolution_list[surface_index]
            flow_variable = self.surface[surface_name].pressure_coefficient
            if main_axes[surface_index] == 0:
                x = self.surface[surface_name].y_local
                y = self.surface[surface_name].z_local
                z = self.surface[surface_name].x_local
            elif main_axes[surface_index] == 1:
                x = self.surface[surface_name].x_local
                y = self.surface[surface_name].z_local
                z = self.surface[surface_name].y_local
            elif main_axes[surface_index] == 2:
                x = self.surface[surface_name].x_local
                y = self.surface[surface_name].y_local
                z = self.surface[surface_name].z_local
            # Trasform to cylindrical coordinates
            r = np.sqrt(x**2 + y**2)
            r_mean = np.mean(r)
            theta = np.arctan2(y,x)*r_mean
            # Create a meshgrid for interpolation over the (theta,z) domain
            x_image = np.linspace(np.min(theta), np.max(theta), int(image_resolution[1]))
            y_image = np.linspace(np.min(z), np.max(z), int(image_resolution[0]))
            X, Y = np.meshgrid(x_image, y_image)
            # Interpolate and extrapolate the data
            Interpolated_Flow_Variable = np.zeros_like(X)*np.nan
            Interpolated_Flow_Variable = griddata((theta,z), flow_variable, (X, Y), method="linear")
            outside_indices = np.isnan(Interpolated_Flow_Variable)
            Interpolated_Flow_Variable[outside_indices] = griddata((theta,z), flow_variable, (X[outside_indices], Y[outside_indices]), method="nearest")
            # Assign data
            self.surface[surface_name].theta = theta
            self.surface[surface_name].z = z
            self.surface[surface_name].image = Interpolated_Flow_Variable
        return
    
    def create_image_block(self,surface_names):
        hor_nans = np.nan*np.ones(shape=(1,self.surface[surface_names[0]].image.shape[1]))
        if len(surface_names) == 1:
            block = np.vstack((hor_nans, self.surface[surface_names[0]].image, hor_nans))
        elif len(surface_names) == 2:
            block = np.vstack((self.surface[surface_names[0]].image, hor_nans, self.surface[surface_names[1]].image, hor_nans))
        elif len(surface_names) == 3:
            block = np.vstack((self.surface[surface_names[0]].image, hor_nans, self.surface[surface_names[1]].image, hor_nans, self.surface[surface_names[2]].image))
        return block
    
    def create_image_blocks(self):
        blocks = []
        blocks.append(self.create_image_block(["ironcub_right_turbine"]))
        blocks.append(self.create_image_block(["ironcub_head"]))
        blocks.append(self.create_image_block(["ironcub_root_link","ironcub_torso_pitch","ironcub_torso_roll"]))
        blocks.append(self.create_image_block(["ironcub_left_turbine"]))
        blocks.append(self.create_image_block(["ironcub_right_back_turbine"]))
        blocks.append(self.create_image_block(["ironcub_torso"]))
        blocks.append(self.create_image_block(["ironcub_left_back_turbine"]))
        blocks.append(self.create_image_block(["ironcub_right_leg_lower"]))
        blocks.append(self.create_image_block(["ironcub_right_leg_pitch","ironcub_right_leg_yaw","ironcub_right_leg_upper"]))
        blocks.append(self.create_image_block(["ironcub_left_leg_pitch","ironcub_left_leg_yaw","ironcub_left_leg_upper"]))
        blocks.append(self.create_image_block(["ironcub_left_leg_lower"]))
        blocks.append(self.create_image_block(["ironcub_right_arm_pitch","ironcub_right_arm_roll"]))
        blocks.append(self.create_image_block(["ironcub_right_arm"]))
        blocks.append(self.create_image_block(["ironcub_left_arm"]))
        blocks.append(self.create_image_block(["ironcub_left_arm_pitch","ironcub_left_arm_roll"]))
        return blocks
    
    def assemble_images(self):
        blocks = self.create_image_blocks()
        vert_nan = np.nan*np.ones(shape=(blocks[0].shape[0],1))
        vert_nan_short = np.nan*np.ones(shape=(blocks[-1].shape[0],1))
        hor_nan = np.nan*np.ones(shape=(1,4*blocks[0].shape[1]+3))
        self.image = np.block([
            [blocks[0], vert_nan, blocks[1], vert_nan, blocks[2], vert_nan, blocks[3]],
            [hor_nan],
            [blocks[4], vert_nan, blocks[5], vert_nan, vert_nan, blocks[6]],
            [hor_nan],
            [blocks[7], vert_nan, blocks[8], vert_nan, blocks[9], vert_nan, blocks[10]],
            [hor_nan],
            [blocks[11], vert_nan_short, blocks[12], vert_nan_short, blocks[13], vert_nan_short, blocks[14]],
        ])
        return

    def plot_surface_contour(self, flow_variable, robot_meshes):
        points = np.vstack((self.x,self.y,self.z)).T # 3D points
        # Normalize the colormap
        # norm = plt.Normalize(vmin=np.min(flow_variable), vmax=np.max(flow_variable))
        norm = plt.Normalize(vmin=-2, vmax=1)
        normalized_flow_variable = norm(flow_variable)
        colormap = cm.jet
        colors = colormap(normalized_flow_variable)[:,:3]
        # Create the point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)
        point_cloud.colors = o3d.utility.Vector3dVector(colors)
        # Create the global frame
        world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])
        # create the relative wind direction vector
        wind_vector = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius=0.01, cone_radius=0.02, cylinder_height=0.2, cone_height=0.04)
        wind_vector.paint_uniform_color([0, 0.5, 1]) # green-ish blue
        wind_vector.rotate(R.from_euler('y', 180, degrees=True).as_matrix(), center=[0, 0, 0])
        wind_vector.translate([0, 0.2, 1.0])
        wind_vector.compute_vertex_normals()
        # Assemble the geometries list
        geometries = [
            {"name": "world_frame", "geometry": world_frame},
            {"name": "wind_vector", "geometry": wind_vector},
        ]
        for mesh_index, mesh in enumerate(robot_meshes):
            #Color meshes with the flow_variable using griddata
            vertices = np.asarray(mesh["mesh"].vertices)
            # Interpolate the data
            mesh_flow_values = griddata((self.x, self.y, self.z), flow_variable, vertices, method="linear")
            # Extrapolate the data using nearest neighbors
            outside_indices = np.isnan(mesh_flow_values)
            mesh_flow_values[outside_indices] = griddata((self.x, self.y, self.z), flow_variable, vertices[outside_indices], method="nearest")
            normalized_mesh_flow_values = norm(mesh_flow_values)
            mesh_colors = colormap(normalized_mesh_flow_values)[:,:3]
            mesh["mesh"].vertex_colors = o3d.utility.Vector3dVector(mesh_colors)
            # Add meshes to the geometries list
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"]})
            print(f"Mesh {mesh['name']} added to the scene.")
        o3d.visualization.draw(geometries,show_skybox=False)
        return
    
    def plot_surface_pointcloud(self, flow_variable, robot_meshes):
        points = np.vstack((self.x,self.y,self.z)).T # 3D points
        # Normalize the colormap
        # norm = plt.Normalize(vmin=np.min(flow_variable), vmax=np.max(flow_variable))
        norm = plt.Normalize(vmin=-2, vmax=1)
        normalized_flow_variable = norm(flow_variable)
        colormap = cm.jet
        colors = colormap(normalized_flow_variable)[:,:3]
        # Create the point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)
        point_cloud.colors = o3d.utility.Vector3dVector(colors)
        # Create the global frame
        world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])
        # create the relative wind direction vector
        wind_vector = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius=0.01, cone_radius=0.02, cylinder_height=0.2, cone_height=0.04)
        wind_vector.paint_uniform_color([0, 0.5, 1]) # green-ish blue
        wind_vector.rotate(R.from_euler('y', 180, degrees=True).as_matrix(), center=[0, 0, 0])
        wind_vector.translate([0, 0.2, 1.0])
        wind_vector.compute_vertex_normals()
        # Create transparent mesh material
        mesh_material = o3d.visualization.rendering.MaterialRecord()
        mesh_material.shader = "defaultLitTransparency"
        mesh_material.base_color = [0.5, 0.5, 0.5, 0.5]  # RGBA, A is for alpha
        # Assemble the geometries list
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "world_frame", "geometry": world_frame},
            {"name": "wind_vector", "geometry": wind_vector},
        ]
        for mesh_index, mesh in enumerate(robot_meshes):
            # Add meshes to the geometries list
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"], "material": mesh_material})
            print(f"Mesh {mesh['name']} added to the scene.")
        o3d.visualization.draw(geometries,show_skybox=False)
        return

class FlowGenerator:
    def __init__(self, robot_name) -> None:
        self.database_path = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[8:] / "database-extended"
        self.surface = {}
        self.x = np.empty(shape=(0,))
        self.y = np.empty(shape=(0,))
        self.z = np.empty(shape=(0,))
        self.cp = np.empty(shape=(0,))
        self.fx = np.empty(shape=(0,))
        self.fy = np.empty(shape=(0,))
        self.fz = np.empty(shape=(0,))
        self.image = np.empty(shape=(0,0))
    
    def separate_horizontal_blocks(self, image):
        horizontal_blocks = []
        block = np.empty(shape=(0,image.shape[1]))
        for row in range(image.shape[0]):
            if len(np.where(np.isnan(image[row,:]))[0]) < image.shape[1]:
                block = np.vstack((block,image[row,:]))
                horizontal_blocks.append(block) if row == image.shape[0]-1 else None
            elif len(np.where(np.isnan(image[row,:]))[0]) == image.shape[1]:
                horizontal_blocks.append(block) if block.shape[0] > 0 else None
                block = np.empty(shape=(0,image.shape[1]))
        return horizontal_blocks
    
    def separate_vertical_blocks(self, image):
        vertical_blocks = []
        block = np.empty(shape=(image.shape[0],0))
        for col in range(image.shape[1]):
            if len(np.where(np.isnan(image[:,col]))[0]) < image.shape[0]:
                block = np.hstack((block,image[:,col].reshape(-1,1)))
                vertical_blocks.append(block) if col == image.shape[1]-1 else None
            elif len(np.where(np.isnan(image[:,col]))[0]) == image.shape[0]:
                vertical_blocks.append(block) if block.shape[1] > 0 else None
                block = np.empty(shape=(image.shape[0],0))
        return vertical_blocks
    
    def assign_images_to_surfaces(self, images):
        images_order = [
            "ironcub_right_turbine", 
            "ironcub_head",
            "ironcub_root_link","ironcub_torso_pitch","ironcub_torso_roll",
            "ironcub_left_turbine",
            "ironcub_right_back_turbine",
            "ironcub_torso",
            "ironcub_left_back_turbine",
            "ironcub_right_leg_lower",
            "ironcub_right_leg_pitch","ironcub_right_leg_yaw","ironcub_right_leg_upper",
            "ironcub_left_leg_pitch","ironcub_left_leg_yaw","ironcub_left_leg_upper",
            "ironcub_left_leg_lower",
            "ironcub_right_arm_pitch","ironcub_right_arm_roll",
            "ironcub_right_arm",
            "ironcub_left_arm",
            "ironcub_left_arm_pitch","ironcub_left_arm_roll"
        ]
        blocks_dict = {}
        for image_index, image_name in enumerate(images_order):
            blocks_dict[image_name] = images[image_index]
        return blocks_dict
    
    def separate_images(self, image):
        self.image = image
        blocks = []
        horizontal_blocks = self.separate_horizontal_blocks(image)
        for block in horizontal_blocks:
            sub_blocks = self.separate_vertical_blocks(block)
            for sub_block in sub_blocks:
                sub_sub_blocks = self.separate_horizontal_blocks(sub_block)
                for sub_sub_block in sub_sub_blocks:
                    blocks.append(sub_sub_block)
        blocks_dict = self.assign_images_to_surfaces(blocks)
        for surface_name, image in blocks_dict.items():
            self.surface[surface_name] = SurfaceData()
            self.surface[surface_name].image = image
        return
    
    def transform_points(self, frame_1_H_frame_2, x, y, z):
        ones = np.ones((len(x),))
        starting_coordinates = np.vstack((x,y,z,ones)).T
        ending_coordinates = np.dot(frame_1_H_frame_2,starting_coordinates.T).T
        return ending_coordinates[:,0], ending_coordinates[:,1], ending_coordinates[:,2]

    def get_surface_mesh_points(self, surface_list, link_H_world_ref_dict, world_H_link_dict, joint_config_name_ref="flight30", pitch_angle_ref=30, yaw_angle_ref=0):
        for surface_name in surface_list:
            database_file_path = str(self.database_path / f"{joint_config_name_ref}-{pitch_angle_ref}-{yaw_angle_ref}-{surface_name}.dtbs")
            data = np.loadtxt(database_file_path, skiprows=1)
            x_global = data[:,1]
            y_global = data[:,2]
            z_global = data[:,3]
            # transform the data from world to reference link frame
            self.surface[surface_name].x_local, self.surface[surface_name].y_local, self.surface[surface_name].z_local = self.transform_points(
                link_H_world_ref_dict[surface_name],x_global,y_global,z_global
                )
            # compute the transformation from the link frame to the current world frame
            self.surface[surface_name].x_global, self.surface[surface_name].y_global, self.surface[surface_name].z_global = self.transform_points(
                world_H_link_dict[surface_name],
                self.surface[surface_name].x_local,
                self.surface[surface_name].y_local,
                self.surface[surface_name].z_local
                )
        return
    
    def interpolate_flow_data_2D(self, surface_list, main_axes):
        for surface_index, surface_name in enumerate(surface_list):
            if main_axes[surface_index] == 0:
                x = self.surface[surface_name].y_local
                y = self.surface[surface_name].z_local
                z = self.surface[surface_name].x_local
            elif main_axes[surface_index] == 1:
                x = self.surface[surface_name].x_local
                y = self.surface[surface_name].z_local
                z = self.surface[surface_name].y_local
            elif main_axes[surface_index] == 2:
                x = self.surface[surface_name].x_local
                y = self.surface[surface_name].y_local
                z = self.surface[surface_name].z_local
            # Trasform to cylindrical coordinates
            r = np.sqrt(x**2 + y**2)
            r_mean = np.mean(r)
            theta = np.arctan2(y,x)*r_mean
            # Create a meshgrid for interpolation
            x_image = np.linspace(np.min(theta), np.max(theta), self.surface[surface_name].image.shape[1])
            y_image = np.linspace(np.min(z), np.max(z), self.surface[surface_name].image.shape[0])
            X, Y = np.meshgrid(x_image, y_image)
            points = np.vstack((X.ravel(),Y.ravel())).T
            flow_variable = self.surface[surface_name].image.ravel()
            # Interpolate and extrapolate the data from the image
            Interpolated_Flow_Variable = np.zeros_like(theta)*np.nan
            Interpolated_Flow_Variable = griddata(points, flow_variable, (theta,z), method="linear")
            outside_indices = np.isnan(Interpolated_Flow_Variable)
            Interpolated_Flow_Variable[outside_indices] = griddata(points, flow_variable, (theta[outside_indices], z[outside_indices]), method="nearest")
            self.surface[surface_name].pressure_coefficient = Interpolated_Flow_Variable
            # Assign data
            self.surface[surface_name].theta = theta
            self.surface[surface_name].z = z
            self.x = np.append(self.x, self.surface[surface_name].x_global)
            self.y = np.append(self.y, self.surface[surface_name].y_global)
            self.z = np.append(self.z, self.surface[surface_name].z_global)
            self.cp = np.append(self.cp,self.surface[surface_name].pressure_coefficient)
        return

    def plot_surface_pointcloud(self, flow_variable, meshes):
        points = np.vstack((self.x,self.y,self.z)).T # 3D points
        # Normalize the colormap
        # norm = plt.Normalize(vmin=np.min(flow_variable), vmax=np.max(flow_variable))
        norm = plt.Normalize(vmin=-2, vmax=1)
        normalized_flow_variable = norm(flow_variable)
        colormap = cm.jet
        colors = colormap(normalized_flow_variable)[:,:3]
        # Create the point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)
        point_cloud.colors = o3d.utility.Vector3dVector(colors)
        # Create the global frame
        world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])
        # create the relative wind direction vector
        wind_vector = o3d.geometry.TriangleMesh.create_arrow(cylinder_radius=0.01, cone_radius=0.02, cylinder_height=0.2, cone_height=0.04)
        wind_vector.paint_uniform_color([0, 0.5, 1]) # green-ish blue
        wind_vector.rotate(R.from_euler('y', 180, degrees=True).as_matrix(), center=[0, 0, 0])
        wind_vector.translate([0, 0.2, 1.0])
        wind_vector.compute_vertex_normals()
        # Create transparent mesh material
        transparent_material = o3d.visualization.rendering.MaterialRecord()
        transparent_material.shader = "defaultLitTransparency"
        transparent_material.base_color = [0.5, 0.5, 0.5, 0.7]  # RGBA, A is for alpha
        # Assemble the geometries list
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "world_frame", "geometry": world_frame},
            {"name": "wind_vector", "geometry": wind_vector},
        ]
        for mesh_index, mesh in enumerate(meshes):
            # Add meshes to the geometries list
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"], "material": transparent_material})
            print(f"Mesh {mesh['name']} added to the scene.")
        o3d.visualization.draw(geometries,show_skybox=False)
        return