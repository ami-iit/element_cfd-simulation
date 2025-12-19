"""
Author: Antonello Paolino
Date: 2025-05-12
Description:    This code uses the pyAnsys geometry package to load the robot
                CAD model and modify the joint configuration.
"""

from csv import reader
from pathlib import Path
import numpy as np
import idyntree.bindings as idyntree

from ansys.geometry.core import launch_modeler_with_discovery
from ansys.geometry.core.misc.options import ImportOptions
from ansys.geometry.core.misc.measurements import UNITS, DEFAULT_UNITS
from ansys.geometry.core.math import Point3D, Vector3D, UNITVECTOR3D_X

# set default units for geometry measurements
DEFAULT_UNITS.LENGTH = UNITS.mm
DEFAULT_UNITS.ANGLE = UNITS.deg


def main():
    robot_name = "iRonCub-Mk3"
    # get input files
    root = Path(__file__).parents[0]

    urdf_path = r"C:\Users\apaolino\code\ironcub-software-ws\src\component_ironcub\models\iRonCub-Mk3\iRonCub\robots\iRonCub-Mk3\model_stl.urdf"
    stp_dir = r"C:\Users\apaolino\code\element_cfd-simulation\simulations\pyfluent\input\iRonCub-Mk3\iRonCub\meshes\stp"

    # load robot model
    model_loader = idyntree.ModelLoader()
    model_loader.loadModelFromFile(urdf_path)
    model = model_loader.model()
    kindyn = idyntree.KinDynComputations()
    kindyn.loadRobotModel(model)

    # import links
    # set zero position
    kindyn.setRobotState(
        np.eye(4),
        np.zeros(kindyn.getNrOfDegreesOfFreedom()),
        np.zeros(6),
        np.zeros(kindyn.getNrOfDegreesOfFreedom()),
        np.zeros(3),
    )
    visuals = model.visualSolidShapes().getLinkSolidShapes()
    links = {}
    for link_id in range(model.getNrOfLinks()):
        link_name = model.getLinkName(link_id)
        if visuals[link_id] == ():  # no visual
            continue
        link_visual = visuals[link_id][0]
        if link_visual.isExternalMesh():
            mesh_path = link_visual.asExternalMesh().getFileLocationOnLocalFileSystem()
            stp_path = Path(stp_dir) / (Path(mesh_path).stem + ".stp")
            l_H_g = link_visual.getLink_H_geometry().asHomogeneousTransform().toNumPy()
            links[link_name] = {"stp_path": stp_path, "l_H_g": l_H_g}

    # launch discovery modeler to assemble robot
    modeler = launch_modeler_with_discovery(hidden=False)
    design = modeler.create_design(robot_name)

    for link in links:
        stp_path = links[link]["stp_path"]
        l_H_g = links[link]["l_H_g"]
        if not stp_path.exists():
            print(f"STP file for link {link} not found: {stp_path}")
            continue
        # import step file
        component = design.insert_file(stp_path)
        faces = []
        for body in component.bodies:
            # compute world to geometry transform
            w_H_l = kindyn.getWorldTransform(link).asHomogeneousTransform().toNumPy()
            w_H_g = w_H_l @ l_H_g
            # rotate body to correct orientation
            w_R_g = w_H_g[0:3, 0:3]
            angle = np.arccos((np.trace(w_R_g) - 1) / 2)
            if angle > 0 or angle < 0:
                axis = (
                    1
                    / (2 * np.sin(angle))
                    * np.array(
                        [
                            w_R_g[2, 1] - w_R_g[1, 2],
                            w_R_g[0, 2] - w_R_g[2, 0],
                            w_R_g[1, 0] - w_R_g[0, 1],
                        ]
                    )
                )
                axis_direction = Vector3D(axis / np.linalg.norm(axis))
                axis_origin = Point3D(np.zeros(3))
                body.rotate(
                    axis_origin, axis_direction=axis_direction, angle=np.degrees(angle)
                )
            # translate body to correct position
            pos = w_H_g[0:3, 3] * 1000  # in mm
            dist = np.linalg.norm(pos)
            if dist > 0:
                direction = Vector3D(pos / dist)
                body.translate(direction=direction, distance=dist)
            faces.extend(body.faces)
        # create named selection for the link
        design.create_named_selection(name=link, faces=faces)

    input("Press Enter to continue...")
    print("checkpoint")


if __name__ == "__main__":
    main()
