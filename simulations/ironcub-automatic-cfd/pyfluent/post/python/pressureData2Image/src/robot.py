from idyntree import bindings as idyntree
import os
import pathlib
import open3d as o3d
import numpy as np
from scipy.spatial.transform import Rotation as R
import toml

class Robot:
    def __init__(self, robot_name):
        self.name = robot_name
        self._set_model_paths()
        self._load_configuration()
        self.kinDyn = self._load_kinDyn()
        
    def _set_model_paths(self):
        self.config_path = pathlib.Path(__file__).parents[1] / "config" / f"{self.name}.toml"
        component_path = pathlib.Path(os.getenv("IRONCUB_COMPONENT_SOURCE_DIR"))
        self.model_path = component_path / "models" / f"{self.name}" / "iRonCub" / "robots" / f"{self.name}_Gazebo" / "model_stl.urdf"
        self.mesh_path = component_path / "models" / f"{self.name}" / "iRonCub" / "meshes" / "stl"
        
    def _load_configuration(self):
        self.config = toml.load(self.config_path)
        self.joint_list = self.config["Joints"]["List"]
        self.base_link = self.config["Model"]["Base_link"]
        self.surface_list = self.config["Surfaces"]["List"]
        self.surface_frames = self.config["Surfaces"]["Frames"]
        self.surface_axes = self.config["Surfaces"]["Axes"]
        self.rotation_angles = self.config["Surfaces"]["Rot"]
        self.image_resolutions = self.config["Surfaces"]["Resolutions"]
    
    def _load_kinDyn(self):
        print(f"[loadReducedModel]: loading the following model: {self.model_path}")
        model_loader = idyntree.ModelLoader()
        reduced_model = model_loader.model()
        model_loader.loadReducedModelFromFile(str(self.model_path), self.joint_list)
        self.nDOF = reduced_model.getNrOfDOFs()
        kinDyn = idyntree.KinDynComputations()
        kinDyn.loadRobotModel(reduced_model)
        kinDyn.setFloatingBase(self.base_link)
        print(f'[loadReducedModel]: loaded model: {self.model_path}, number of joints: {self.nDOF}')
        return kinDyn
    
    def set_state(self, pitch_angle, yaw_angle, joint_positions):
        # Compute base pose
        world_R_base = R.from_euler('zxy', [-90, -pitch_angle, yaw_angle], degrees=True).as_matrix()
        base_pose = np.block([
            [world_R_base, np.zeros((3, 1))],
            [np.zeros((1, 3)), np.ones((1, 1))]
        ])
        # Set unused variables
        joint_velocities = np.zeros_like(joint_positions)
        base_velocity  = np.zeros(6)
        gravity_acceleration  = np.array([0,0,9.81])
        # Set robot state
        ack1 = self.kinDyn.setRobotState(base_pose, joint_positions, base_velocity, joint_velocities, gravity_acceleration)
        # Check if the robot state is set correctly #2
        joint_positions_iDynTree = idyntree.VectorDynSize(len(joint_positions))
        self.kinDyn.getJointPos(joint_positions_iDynTree)
        val = np.linalg.norm(joint_positions - joint_positions_iDynTree.toNumPy())
        ack2 = val < 1e-6
        if not ack1 and not ack2:
            print("[setRobotState]: error in setting robot state.")
        return
    
    def visualize(self):
        viz = idyntree.Visualizer()
        if viz.addModel(self.kinDyn.model(), self.name):
            print("[initializeVisualizer]: model loaded in the visualizer.")
        else:
            print("[initializeVisualizer]: unable to load the model in the visualizer.")
        viz.camera().animator().enableMouseControl(True)
        base_pose = self.kinDyn.getWorldBaseTransform().asHomogeneousTransform().toNumPy()
        joint_positions = idyntree.VectorDynSize(self.nDOF)
        self.kinDyn.getJointPos(joint_positions)
        viz.modelViz(self.name).setPositions(base_pose, joint_positions)
        while viz.run():
            viz.draw()
        return
    
    def compute_world_to_link_transform(self, frame_name, rotation_angle):
        world_H_link = self.kinDyn.getWorldTransform(frame_name).asHomogeneousTransform().toNumPy()
        frame_rotation_matrix = R.from_euler('z', rotation_angle, degrees=True).as_matrix()
        world_H_link[:3,:3] = np.dot(world_H_link[0:3,0:3], frame_rotation_matrix)
        return world_H_link
    
    def invert_homogeneous_transform(self, a_H_b):
        a_R_b = a_H_b[0:3,0:3]
        a_d_b = a_H_b[0:3,-1]
        b_H_a = np.block([
            [a_R_b.T, np.dot(-a_R_b.T, a_d_b).reshape((3, 1))],
            [np.zeros((1, 3)), np.ones((1, 1))]
        ])
        return b_H_a
    
    def get_links_and_meshes(self):
        self.links_list = []
        self.meshes_list = []
        self.link_H_geom = [] 
        model = self.kinDyn.getRobotModel()
        visual = model.visualSolidShapes().getLinkSolidShapes()
        nr_of_links = visual.size()
        iterator = visual.begin()
        for link_index in range(nr_of_links):
            link_name = model.getLinkName(link_index)
            solidarray = iterator.next()
            solids_number = len(solidarray)
            for solid_index in range(solids_number):
                if solidarray[solid_index].isExternalMesh():
                    mesh_name = solidarray[solid_index].asExternalMesh().getFilename()
                    link_H_geom = solidarray[solid_index].getLink_H_geometry().asHomogeneousTransform().toNumPy()
                    self.links_list.append(link_name)
                    self.meshes_list.append(mesh_name.split("/")[-1].split(".")[0])
                    self.link_H_geom.append(link_H_geom)
        return

    def load_mesh(self):
        # Iterate over the mesh list
        self.get_links_and_meshes()
        meshes = []
        for mesh_index, mesh_name in enumerate(self.meshes_list):
            mesh_path = str(self.mesh_path / f"{mesh_name}.stl")
            mesh = o3d.io.read_triangle_mesh(mesh_path)
            # Transform the mesh dimensions from m to mm
            mesh.scale(0.001, center=[0, 0, 0])
            # Get the world to mesh frame homogeneous transformation
            mesh_frame = self.links_list[mesh_index]
            world_H_frame = self.compute_world_to_link_transform(frame_name=mesh_frame, rotation_angle=0)
            frame_H_geom = self.link_H_geom[mesh_index]
            world_H_geom = np.dot(world_H_frame, frame_H_geom)
            mesh.transform(world_H_geom)
            # Compute the vertex normals
            mesh.compute_vertex_normals()
            # store the mesh
            meshes.append({"name": mesh_name, "mesh": mesh})
        return meshes
