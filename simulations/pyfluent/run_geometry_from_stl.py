"""
Author: Antonello Paolino
Date: 2025-05-12
Description:    This code uses the pyAnsys geometry package to load the robot
                CAD model and modify the joint configuration.
"""

from pathlib import Path
import numpy as np
import idyntree.bindings as idyntree
import trimesh
from OCC.Core.StlAPI import StlAPI_Reader
from OCC.Core.TopoDS import TopoDS_Shell, TopoDS_Solid, TopoDS_Compound
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SHELL
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCC.Core.ShapeFix import ShapeFix_Solid
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_ManifoldSolidBrep
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Interface import Interface_Static_SetCVal

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
    stl_path = r"C:\Users\apaolino\code\ironcub-software-ws\src\component_ironcub\models\iRonCub-Mk3\iRonCub\meshes\stl"

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
    stl_meshes = {}
    for link_id in range(model.getNrOfLinks()):
        link_name = model.getLinkName(link_id)
        if visuals[link_id] == ():  # no visual
            continue
        link_visual = visuals[link_id][0]
        if link_visual.isExternalMesh():
            mesh_path = link_visual.asExternalMesh().getFileLocationOnLocalFileSystem()
            file_path = Path(stl_path) / Path(mesh_path).name
            l_H_g = link_visual.getLink_H_geometry().asHomogeneousTransform().toNumPy()
            stl_meshes[link_name] = {"file_path": file_path, "l_H_g": l_H_g}

    mesh_name = "root_link"
    meshpath = stl_meshes[mesh_name]["file_path"]
    l_H_g = stl_meshes[mesh_name]["l_H_g"]
    # cleaned_stl_path = meshpath.with_name(meshpath.stem + "_cleaned.stl")
    cleaned_stl_path = meshpath
    step_path = cleaned_stl_path.with_suffix(".step")

    # check the mesh with trimesh
    m = trimesh.load_mesh(meshpath)
    print("Watertight:", m.is_watertight)
    # m.remove_unreferenced_vertices()
    # m.remove_degenerate_faces()
    # m.fix_normals()
    # m.fill_holes()  # small holes only
    # m.merge_vertices()  # weld close vertices
    # m.export(str(cleaned_stl_path))
    # 1) Read triangulated STL into a compound
    reader = StlAPI_Reader()
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)
    ok = reader.Read(comp, str(cleaned_stl_path))
    if not ok:
        raise RuntimeError(f"Failed to read STL: {cleaned_stl_path}")
    # 2) Sew faces into a watertight shell
    #    Adjust sew_tol to your model scale (in mm). Start with 1e-3; increase if tiny gaps remain.
    sew_tol = 1.0e-3
    sew = BRepBuilderAPI_Sewing(sew_tol, True, True, True, True)
    sew.Load(comp)
    sew.Perform()
    sewn = sew.SewedShape()
    # Collect shells produced by sewing (common case: one shell)
    shells = []
    exp = TopExp_Explorer(sewn, TopAbs_SHELL)
    while exp.More():
        current_shape = exp.Current()
        if isinstance(current_shape, TopoDS_Shell):
            shells.append(current_shape)
        exp.Next()
    # If explorer found none, maybe the sewed shape *is itself* a shell
    if not shells and isinstance(sewn, TopoDS_Shell):
        shells = [sewn]
    if not shells:
        raise RuntimeError(
            "No shell found after sewing — mesh likely not watertight or sew_tol too small."
        )
    # 3) Make solids from shells, heal, and validate
    solids = []
    for sh in shells:
        mk_solid = BRepBuilderAPI_MakeSolid(sh)
        if not mk_solid.IsDone():
            raise RuntimeError(
                "BRepBuilderAPI_MakeSolid failed — try a larger sew_tol or repair the STL more."
            )
        solid = mk_solid.Solid()
        # Heal & validate
        fixer = ShapeFix_Solid()
        fixer.Init(solid)
        fixer.Perform()
        solid_fixed = fixer.Solid()
        if not BRepCheck_Analyzer(solid_fixed).IsValid():
            raise RuntimeError(
                "Solid invalid — increase sew_tol slightly (e.g., 5e-3) or improve STL cleanup."
            )
        solids.append(solid_fixed)
    if not solids:
        raise RuntimeError("No solids created from the sewn shell(s).")
    # 4) Write AP242 STEP in millimeters
    Interface_Static_SetCVal("write.step.schema", "AP242")
    Interface_Static_SetCVal("write.step.unit", "MM")
    writer = STEPControl_Writer()
    for s in solids:
        writer.Transfer(s, STEPControl_ManifoldSolidBrep)
    status = writer.Write(str(step_path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: {step_path}")
    print(f"STEP written: {step_path}  | solids: {len(solids)}  | sew_tol: {sew_tol}")

    # launch discovery modeler
    modeler = launch_modeler_with_discovery(hidden=False)
    design = modeler.create_design(robot_name)
    # import step
    design.insert_file(str(step_path))
    component = design.components[0]
    body = component.bodies[0]

    w_H_l = kindyn.getWorldTransform(mesh_name).asHomogeneousTransform().toNumPy()
    w_H_g = w_H_l @ l_H_g

    pos = w_H_g[0:3, 3] * 1000  # in mm
    dist = np.linalg.norm(pos)
    body.translate(direction=Vector3D(pos / dist), distance=dist)

    # reopen modeler
    modeler = launch_modeler_with_discovery(hidden=False)
    design = modeler.open_file(root / f"{robot_name}.dsco")
    component = design.components[0]

    print("checkpoint")


if __name__ == "__main__":
    main()
