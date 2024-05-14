import idyntree.bindings as idyntree
import os
import numpy as np


def loadReducedModel(jointList: list, baseLinkName: str, modelFilePath: str, debugMode: str) -> dict[str, idyntree.KinDynComputations]:

    ## INITIALIZATION
    print(f"[loadReducedModel]: loading the following model: {modelFilePath}")

    kinDynModel = {}

    # if DEBUG option is set to TRUE, all the wrappers will be run in debug
    # mode. Wrappers concerning iDyntree simulator have their own debugger
    kinDynModel["DEBUG"] = debugMode

    # retrieve the link that will be used as the floating base
    kinDynModel["BASE_LINK"] = baseLinkName

    # # load the list of joints to be used in the reduced model
    # jointList_iDynTree = idyntree.StringVector()
    # for joint in jointList:
    #     jointList_iDynTree.push_back(joint)

    # only joints specified in the joint list will be considered in the model
    modelLoader = idyntree.ModelLoader()
    reducedModel = modelLoader.model()

    modelLoader.loadReducedModelFromFile(f"{modelFilePath}", jointList)

    # get the number of degrees of freedom of the reduced model
    kinDynModel["NDOF"] = reducedModel.getNrOfDOFs()

    # initialize the iDyntree KinDynComputation class, that will be used for
    # computing the floating base system state, dynamics, and kinematics
    kinDynModel["kinDynComp"] = idyntree.KinDynComputations()

    kinDynModel["kinDynComp"].loadRobotModel(reducedModel)

    # set the floating base link
    kinDynModel["kinDynComp"].setFloatingBase(kinDynModel["BASE_LINK"])

    print(
        f'[loadReducedModel]: loaded model: {modelFilePath}, number of joints: {kinDynModel["NDOF"]}'
    )

    return kinDynModel

