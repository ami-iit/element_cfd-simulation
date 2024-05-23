from idyntree import bindings as idyntree
import os
import pathlib
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
        self.surface_meshes = self.config["Surfaces"]["Meshes"]
        self.rotation_angles = self.config["Surfaces"]["Rotation_angles"]
    
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
    
    def invert_homogeneous_transform(self, a_H_b):
        a_R_b = a_H_b[0:3,0:3]
        a_d_b = a_H_b[0:3,-1]
        b_H_a = np.block([
            [a_R_b.T, np.dot(-a_R_b.T, a_d_b).reshape((3, 1))],
            [np.zeros((1, 3)), np.ones((1, 1))]
        ])
        return b_H_a