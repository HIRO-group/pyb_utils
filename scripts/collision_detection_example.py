#!/usr/bin/env python
"""Example demonstrating collision detection and shortest distance queries."""
import numpy as np
import pybullet as pyb
import pybullet_data

from pyb_utils.collision import NamedCollisionObject, CollisionDetector


def load_environment(client_id):
    pyb.setAdditionalSearchPath(
        pybullet_data.getDataPath(), physicsClientId=client_id
    )

    # ground plane
    ground_id = pyb.loadURDF(
        "plane.urdf", [0, 0, 0], useFixedBase=True, physicsClientId=client_id
    )

    # KUKA iiwa robot arm
    kuka_id = pyb.loadURDF(
        "kuka_iiwa/model.urdf",
        [0, 0, 0],
        useFixedBase=True,
        physicsClientId=client_id,
    )

    # some cubes for obstacles
    cube1_id = pyb.loadURDF(
        "cube.urdf", [1, 1, 0.5], useFixedBase=True, physicsClientId=client_id
    )
    cube2_id = pyb.loadURDF(
        "cube.urdf", [-1, -1, 0.5], useFixedBase=True, physicsClientId=client_id
    )
    cube3_id = pyb.loadURDF(
        "cube.urdf", [1, -1, 0.5], useFixedBase=True, physicsClientId=client_id
    )

    # store body indices in a dict with more convenient key names
    bodies = {
        "robot": kuka_id,
        "ground": ground_id,
        "cube1": cube1_id,
        "cube2": cube2_id,
        "cube3": cube3_id,
    }
    return bodies

def create_user_debug_params(gui_id):
    return {
        'collision_margin': pyb.addUserDebugParameter('collision_margin', 0, 0.2, 0.01, physicsClientId=gui_id),
        'lbr_iiwa_joint1': pyb.addUserDebugParameter('lbr_iiwa_joint1', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint2': pyb.addUserDebugParameter('lbr_iiwa_joint2', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint3': pyb.addUserDebugParameter('lbr_iiwa_joint3', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint4': pyb.addUserDebugParameter('lbr_iiwa_joint4', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint5': pyb.addUserDebugParameter('lbr_iiwa_joint5', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint6': pyb.addUserDebugParameter('lbr_iiwa_joint6', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id),
        'lbr_iiwa_joint7': pyb.addUserDebugParameter('lbr_iiwa_joint7', -2*np.pi, 2*np.pi, 0, physicsClientId=gui_id)
    }

def update_robot_state(robot_id, state, physicsClientId):
    for joint_idx in range(pyb.getNumJoints(robot_id, physicsClientId=physicsClientId)):
        pyb.resetJointState(robot_id, joint_idx, state[joint_idx], physicsClientId=physicsClientId)

def main():

    # main simulation server, with a GUI
    gui_id = pyb.connect(pyb.GUI)

    # simulation server only used for collision detection
    col_id = pyb.connect(pyb.DIRECT)

    # create user debug parameters
    user_params = create_user_debug_params(gui_id)

    # add bodies to both of the environments
    bodies = load_environment(gui_id)
    collision_bodies = load_environment(col_id)

    # define bodies (and links) to use for shortest distance computations and
    # collision checking
    ground = NamedCollisionObject("ground")
    cube1 = NamedCollisionObject("cube1")
    cube2 = NamedCollisionObject("cube2")
    cube3 = NamedCollisionObject("cube3")
    link7 = NamedCollisionObject("robot", "lbr_iiwa_link_7")  # last link

    col_detector = CollisionDetector(
        col_id,
        collision_bodies,
        [(link7, ground), (link7, cube1), (link7, cube2), (link7, cube3)],
    )

    robot_id = bodies["robot"]

    while True:
        # compute shortest distances for a random configuration
        q = np.array([
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint1"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint2"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint3"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint4"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint5"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint6"]),
            pyb.readUserDebugParameter(user_params["lbr_iiwa_joint7"])
        ])
        
        d = col_detector.compute_distances(q)
        in_col = col_detector.in_collision(
            q, 
            margin=pyb.readUserDebugParameter(user_params["collision_margin"]))

        if not in_col:
            update_robot_state(robot_id, q, physicsClientId=gui_id)
        else:
            pyb.addUserDebugText(
                "Avoiding collision",
                textPosition=[0, 0, 1.5],
                textColorRGB=[1, 0, 0],
                textSize=2,
                lifeTime=0.2
            )

        print(f"Distance to obstacles = {d}")

        pyb.stepSimulation(physicsClientId=gui_id)


if __name__ == "__main__":
    main()
