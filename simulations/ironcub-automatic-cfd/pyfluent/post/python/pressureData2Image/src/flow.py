import pathlib
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.interpolate import griddata
from scipy.spatial.transform import Rotation as R

class FlowImporter:
    def __init__(self, robot_name):
        self.database_path = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[8:] / "database-extended"
        self.x = np.empty(shape=(0,))
        self.y = np.empty(shape=(0,))
        self.z = np.empty(shape=(0,))
        self.cp = np.empty(shape=(0,))
        self.fx = np.empty(shape=(0,))
        self.fy = np.empty(shape=(0,))
        self.fz = np.empty(shape=(0,))
        self.images = {}
    
    def import_fluent_data(self,joint_config_name, pitch_angle, yaw_angle, surface_name):
        # load data from the database file
        database_file_path = str(self.database_path / f"{joint_config_name}-{pitch_angle}-{yaw_angle}-{surface_name}.dtbs")
        data = np.loadtxt(database_file_path, skiprows=1)
        # transform the data from the world frame to the link frame
        self.x_global = data[:,1]
        self.y_global = data[:,2]
        self.z_global = data[:,3]
        self.pressure = data[:,4]
        self.x_shear_stress = data[:,5]
        self.y_shear_stress = data[:,6]
        self.z_shear_stress = data[:,7]
        # save link points global coordinates
        self.x = np.append(self.x, self.x_global)
        self.y = np.append(self.y, self.y_global)
        self.z = np.append(self.z, self.z_global)
        return
    
    def transform_fluent_data(self, link_H_world, flow_velocity, flow_density):
        ones = np.ones((len(self.x_global),))
        global_coordinates = np.vstack((self.x_global,self.y_global,self.z_global,ones)).T
        local_coordinates = np.dot(link_H_world,global_coordinates.T).T
        self.x_local = local_coordinates[:,0]
        self.y_local = local_coordinates[:,1]
        self.z_local = local_coordinates[:,2]
        self.pressure_coefficient = self.pressure/(0.5*flow_density*flow_velocity**2)
        self.x_friction_coefficient = self.x_shear_stress/(0.5*flow_density*flow_velocity**2)
        self.y_friction_coefficient = self.y_shear_stress/(0.5*flow_density*flow_velocity**2)
        self.z_friction_coefficient = self.z_shear_stress/(0.5*flow_density*flow_velocity**2)
        # save link points variables
        self.cp = np.append(self.cp, self.pressure_coefficient)
        self.fx = np.append(self.fx, self.x_friction_coefficient)
        self.fy = np.append(self.fy, self.y_friction_coefficient)
        self.fz = np.append(self.fz, self.z_friction_coefficient)
        return
    
    def plot_surface_3D_map_local(self, flow_variable, mesh_path):
        points = np.vstack((self.x_local,self.y_local,self.z_local)).T # 3D points
        # Normalize the colormap
        norm = plt.Normalize(vmin=np.min(flow_variable), vmax=np.max(flow_variable))
        print(np.min(flow_variable), np.max(flow_variable))
        normalized_cp = norm(flow_variable)
        colormap = cm.jet
        colors = colormap(normalized_cp)[:,:3]
        # Create the point cloud
        point_cloud = o3d.geometry.PointCloud()
        point_cloud.points = o3d.utility.Vector3dVector(points)
        point_cloud.colors = o3d.utility.Vector3dVector(colors)
        # Create the local frame
        local_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
        # Load mesh
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        mesh.scale(0.001, center=[0, 0, 0]) # transform the mesh dimensions from m to mm
        mesh.compute_vertex_normals()
        # Apply custom material for transparency
        mesh_material = o3d.visualization.rendering.MaterialRecord()
        mesh_material.shader = "defaultLitTransparency"
        mesh_material.base_color = [0.5, 0.5, 0.5, 0.5]  # RGBA, A is for alpha
        # test
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "local_frame", "geometry": local_frame},
            {"name": "mesh", "geometry": mesh, "material": mesh_material}
        ]
        o3d.visualization.draw(geometries,show_skybox=False)
        return
    
    def plot_surface_point_cloud(self, flow_variable, meshes):
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
        mesh_material.base_color = [0.5, 0.5, 0.5, 0.7]  # RGBA, A is for alpha
        # Assemble the geometries list
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "world_frame", "geometry": world_frame},
            {"name": "wind_vector", "geometry": wind_vector},
        ]
        for mesh_index, mesh in enumerate(meshes):
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"], "material": mesh_material})
        o3d.visualization.draw(geometries,show_skybox=False)
        return

    def interpolate_flow_data(self, flow_variable, main_axis, resolution, surface_name):
        if main_axis == 0:
            x = self.y_local
            y = self.z_local
            z = self.x_local
        elif main_axis == 1:
            x = self.x_local
            y = self.z_local
            z = self.y_local
        elif main_axis == 2:
            x = self.x_local
            y = self.y_local
            z = self.z_local
        # Trasform to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        r_mean = np.mean(r)
        theta = np.arctan2(y,x)*r_mean
        # Create a meshgrid for interpolation
        pixel_nr_x = int(resolution[1])
        pixel_nr_y = int(resolution[0])
        # pixel_nr_x_rounded = round(pixel_nr_x 
        x_image = np.linspace(np.min(theta), np.max(theta), pixel_nr_x)
        y_image = np.linspace(np.min(z), np.max(z), pixel_nr_y)
        X, Y = np.meshgrid(x_image, y_image)
        # Interpolate and extrapolate the data
        Interpolated_Flow_Variable = np.zeros_like(X)*np.nan
        Interpolated_Flow_Variable = griddata((theta,z), flow_variable, (X, Y), method="linear")
        outside_indices = np.isnan(Interpolated_Flow_Variable)
        Interpolated_Flow_Variable[outside_indices] = griddata((theta,z), flow_variable, (X[outside_indices], Y[outside_indices]), method="nearest")
        self.images[surface_name] = Interpolated_Flow_Variable
        return theta, z, X, Y, Interpolated_Flow_Variable
    
    def create_image_block(self,surface_names):
        hor_nans = np.nan*np.ones(shape=(1,self.images[surface_names[0]].shape[1]))
        if len(surface_names) == 1:
            block = np.vstack((hor_nans, self.images[surface_names[0]], hor_nans))
        elif len(surface_names) == 2:
            block = np.vstack((self.images[surface_names[0]], hor_nans, self.images[surface_names[1]], hor_nans))
        elif len(surface_names) == 3:
            block = np.vstack((self.images[surface_names[0]], hor_nans, self.images[surface_names[1]], hor_nans, self.images[surface_names[2]]))
        return block
    
    def create_image_blocks(self):
        blocks = []
        blocks.append(self.create_image_block(["ironcub_head"]))
        blocks.append(self.create_image_block(["ironcub_root_link","ironcub_torso_pitch","ironcub_torso_roll"]))
        blocks.append(self.create_image_block(["ironcub_torso"]))
        blocks.append(self.create_image_block(["ironcub_right_back_turbine"]))
        blocks.append(self.create_image_block(["ironcub_left_back_turbine"]))
        blocks.append(self.create_image_block(["ironcub_right_arm_pitch","ironcub_right_arm_roll","ironcub_right_arm"]))
        blocks.append(self.create_image_block(["ironcub_left_arm_pitch","ironcub_left_arm_roll","ironcub_left_arm"]))
        blocks.append(self.create_image_block(["ironcub_right_turbine"]))
        blocks.append(self.create_image_block(["ironcub_left_turbine"]))
        blocks.append(self.create_image_block(["ironcub_right_leg_pitch","ironcub_right_leg_yaw","ironcub_right_leg_upper"]))
        blocks.append(self.create_image_block(["ironcub_left_leg_pitch","ironcub_left_leg_yaw","ironcub_left_leg_upper"]))
        blocks.append(self.create_image_block(["ironcub_right_leg_lower"]))
        blocks.append(self.create_image_block(["ironcub_left_leg_lower"]))
        return blocks
    
    def assemble_images(self):
        blocks = self.create_image_blocks()
        vert_nan = np.nan*np.ones(shape=(blocks[0].shape[0],1))
        hor_nan = np.nan*np.ones(shape=(1,2*blocks[0].shape[1]+2))
        image = np.block([
            [blocks[0], vert_nan, vert_nan, blocks[1]],
            [hor_nan],
            [vert_nan, blocks[2], vert_nan],
            [hor_nan],
            [blocks[3], vert_nan, vert_nan, blocks[4]],
            [hor_nan],
            [blocks[5], vert_nan, vert_nan, blocks[6]],
            [hor_nan],
            [blocks[7], vert_nan, vert_nan, blocks[8]],
            [hor_nan],
            [blocks[9], vert_nan, vert_nan, blocks[10]],
            [hor_nan],
            [blocks[11], vert_nan, vert_nan, blocks[12]]
        ])
        return image

    def plot_surface_contour(self, flow_variable, meshes):
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
        for mesh_index, mesh in enumerate(meshes):
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
        mesh_material = o3d.visualization.rendering.MaterialRecord()
        mesh_material.shader = "defaultLitTransparency"
        mesh_material.base_color = [0.5, 0.5, 0.5, 0.5]  # RGBA, A is for alpha
        # Assemble the geometries list
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud},
            {"name": "world_frame", "geometry": world_frame},
            {"name": "wind_vector", "geometry": wind_vector},
        ]
        for mesh_index, mesh in enumerate(meshes):
            # Add meshes to the geometries list
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"]})
            print(f"Mesh {mesh['name']} added to the scene.")
        o3d.visualization.draw(geometries,show_skybox=False)
        return

class FlowGenerator:
    def __init__(self, robot_name) -> None:
        self.database_path = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[8:] / "database-extended"
        self.x = np.empty(shape=(0,))
        self.y = np.empty(shape=(0,))
        self.z = np.empty(shape=(0,))
        self.cp = np.empty(shape=(0,))
        self.fx = np.empty(shape=(0,))
        self.fy = np.empty(shape=(0,))
        self.fz = np.empty(shape=(0,))
        self.images = {}
    
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
        blocks_dictionary = {}
        blocks_dictionary["ironcub_head"] = images[0]
        blocks_dictionary["ironcub_root_link"] = images[1]
        blocks_dictionary["ironcub_torso_pitch"] = images[2]
        blocks_dictionary["ironcub_torso_roll"] = images[3]
        blocks_dictionary["ironcub_torso"] = images[4]
        blocks_dictionary["ironcub_right_back_turbine"] = images[5]
        blocks_dictionary["ironcub_left_back_turbine"] = images[6]
        blocks_dictionary["ironcub_right_arm_pitch"] = images[7]
        blocks_dictionary["ironcub_left_arm_pitch"] = images[8]
        blocks_dictionary["ironcub_right_arm_roll"] = images[9]
        blocks_dictionary["ironcub_left_arm_roll"] = images[10]
        blocks_dictionary["ironcub_right_arm"] = images[11]
        blocks_dictionary["ironcub_left_arm"] = images[12]
        blocks_dictionary["ironcub_right_turbine"] = images[13]
        blocks_dictionary["ironcub_left_turbine"] = images[14]
        blocks_dictionary["ironcub_right_leg_pitch"] = images[15]
        blocks_dictionary["ironcub_left_leg_pitch"] = images[16]
        blocks_dictionary["ironcub_right_leg_yaw"] = images[17]
        blocks_dictionary["ironcub_left_leg_yaw"] = images[18]
        blocks_dictionary["ironcub_right_leg_upper"] = images[19]
        blocks_dictionary["ironcub_left_leg_upper"] = images[20]
        blocks_dictionary["ironcub_right_leg_lower"] = images[21]
        blocks_dictionary["ironcub_left_leg_lower"] = images[22]
        return blocks_dictionary
    
    def separate_images(self, image):
        blocks = []
        horizontal_blocks = self.separate_horizontal_blocks(image)
        for block in horizontal_blocks:
            sub_blocks = self.separate_vertical_blocks(block)
            for sub_block in sub_blocks:
                sub_sub_blocks = self.separate_horizontal_blocks(sub_block)
                for sub_sub_block in sub_sub_blocks:
                    blocks.append(sub_sub_block)
        return self.assign_images_to_surfaces(blocks)
    
    def transform_points(self, frame_1_H_frame_2, x, y, z):
        ones = np.ones((len(x),))
        starting_coordinates = np.vstack((x,y,z,ones)).T
        ending_coordinates = np.dot(frame_1_H_frame_2,starting_coordinates.T).T
        return ending_coordinates[:,0], ending_coordinates[:,1], ending_coordinates[:,2]

    def get_surface_mesh_points(self, surface_name, link_H_world_ref, world_H_link_current, joint_config_name_ref="flight30", pitch_angle_ref=30, yaw_angle_ref=0):
        # load data from the database file
        database_file_path = str(self.database_path / f"{joint_config_name_ref}-{pitch_angle_ref}-{yaw_angle_ref}-{surface_name}.dtbs")
        data = np.loadtxt(database_file_path, skiprows=1)
        # get data in the world frame
        self.x_global = data[:,1]
        self.y_global = data[:,2]
        self.z_global = data[:,3]
        # transform the data from world to reference link frame
        self.x_local, self.y_local, self.z_local = self.transform_points(link_H_world_ref,self.x_global,self.y_global,self.z_global)
        # compute the transformation from the link frame to the current world frame
        self.x_global, self.y_global, self.z_global = self.transform_points(world_H_link_current,self.x_local,self.y_local,self.z_local)
        # save link points global coordinates
        self.x = np.append(self.x, self.x_global)
        self.y = np.append(self.y, self.y_global)
        self.z = np.append(self.z, self.z_global)
        return
    
    def interpolate_flow_data_2D(self, image, main_axis, surface_name):
        if main_axis == 0:
            x = self.y_local
            y = self.z_local
            z = self.x_local
        elif main_axis == 1:
            x = self.x_local
            y = self.z_local
            z = self.y_local
        elif main_axis == 2:
            x = self.x_local
            y = self.y_local
            z = self.z_local
        # Trasform to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        r_mean = np.mean(r)
        theta = np.arctan2(y,x)*r_mean
        # Create a meshgrid for interpolation
        x_image = np.linspace(np.min(theta), np.max(theta), image.shape[1])
        y_image = np.linspace(np.min(z), np.max(z), image.shape[0])
        X, Y = np.meshgrid(x_image, y_image)
        points = np.vstack((X.ravel(),Y.ravel())).T
        flow_variable = image.ravel()
        # Interpolate and extrapolate the data from the image
        Interpolated_Flow_Variable = np.zeros_like(theta)*np.nan
        Interpolated_Flow_Variable = griddata(points, flow_variable, (theta,z), method="linear")
        outside_indices = np.isnan(Interpolated_Flow_Variable)
        Interpolated_Flow_Variable[outside_indices] = griddata(points, flow_variable, (theta[outside_indices], z[outside_indices]), method="nearest")
        self.pressure_coefficient = Interpolated_Flow_Variable
        self.cp = np.append(self.cp,Interpolated_Flow_Variable)
        return theta, z, Interpolated_Flow_Variable

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