import pathlib
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.interpolate import griddata
from scipy.spatial.transform import Rotation as R

class Flow:
    def __init__(self, robot_name):
        self.database_path = pathlib.Path(__file__).parents[4] / "solver" / "data" / robot_name[8:] / "database-extended"
        self.x = np.empty(shape=(0,))
        self.y = np.empty(shape=(0,))
        self.z = np.empty(shape=(0,))
        self.cp = np.empty(shape=(0,))
        self.fx = np.empty(shape=(0,))
        self.fy = np.empty(shape=(0,))
        self.fz = np.empty(shape=(0,))
    
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
        # create trnasparent mesh material
        mesh_material = o3d.visualization.rendering.MaterialRecord()
        mesh_material.shader = "defaultLitTransparency"
        mesh_material.base_color = [0.5, 0.5, 0.5, 0.7]  # RGBA, A is for alpha
        # Assemble the geometries list
        geometries = [
            {"name": "point_cloud", "geometry": point_cloud}
        ]
        for mesh_index, mesh in enumerate(meshes):
            geometries.append({"name": f"mesh_{mesh_index}", "geometry": mesh["mesh"], "material": mesh_material})
        o3d.visualization.draw(geometries,show_skybox=False)
        return

    def interpolate_flow_data(self, flow_variable, main_axis, resolution = 800, mask_threshold = 0.1):
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
        pixel_nr_x = int(resolution*(np.max(theta)-np.min(theta)))
        pixel_nr_y = int(resolution*(np.max(z)-np.min(z)))
        x_image = np.linspace(np.min(theta), np.max(theta), pixel_nr_x)
        y_image = np.linspace(np.min(z), np.max(z), pixel_nr_y)
        X, Y = np.meshgrid(x_image, y_image)
        # create mask for points outside the geometry
        min_distances = np.zeros(shape=(0,))
        for x,y in zip(X.flatten(), Y.flatten()):
            distances = np.sqrt((theta-x)**2 + (z-y)**2)
            min_distances = np.append(min_distances, np.min(distances))
        min_distances = min_distances.reshape(X.shape)
        mask_indices = min_distances < mask_threshold
        # Interpolate the data
        Interpolated_Flow_Variable = np.zeros_like(X)*np.nan
        Interpolated_Flow_Variable[mask_indices] = griddata((theta,z), flow_variable, (X[mask_indices], Y[mask_indices]), method='linear')
        return theta, z, X, Y, Interpolated_Flow_Variable
    
    def interpolate_pressure_data(self, main_axis, resolution = (128, 128), mask_threshold = 0.1):
        return self.interpolate_flow_data(self.pressure_coefficient, main_axis, resolution, mask_threshold)
