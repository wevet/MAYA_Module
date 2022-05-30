# -*- coding: utf-8 -*-

from maya import cmds
import maya.OpenMaya as om
import math
import json
import os

"""
usage 
import json_exporter
import importlib
importlib.reload(json_exporter)
json_exporter.save_selected_joints_to_json(1, 4, False)
"""

def save_selected_joints_to_json(start_time, end_time, export_joint: bool):
    base_path = cmds.file(q=True, sceneName=True)
    base_path_list = base_path.split("/")
    current_scene = base_path_list[-1]
    scene_name = current_scene[:-3]

    # Originally, it is a joint, but it gets a transform
    if export_joint:
        objects = cmds.ls(selection=True, type="joint", dag=True, long=True)
    else:
        objects = cmds.ls(selection=True, type="transform", dag=True, long=True)
    joints = {}
    time_range = range(start_time, end_time+1, 1)

    index = 0
    for obj in objects:
        joint_dict = {}
        #short_name = obj.split("|")[-1]
        short_name = 'bone_' + str(index)
        index += 1
        is_root = False
        if "_ROOT_" in short_name:
            is_root = True

        for frame in time_range:
            if is_root:
                joint_dict[frame] = _get_frame_dist_for_root(obj, frame)
            else:
                joint_dict[frame] = _get_frame_dict(obj, frame)
        joints['start'] = start_time
        joints['end'] = end_time
        joints[short_name] = joint_dict
    _export_json(joints, scene_name)

#non root joints should pass values from object space
def _get_frame_dict(obj, frame):
    rot_order = cmds.getAttr('%s.rotateOrder' % obj)
    joint_mat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(cmds.getAttr('%s.matrix' % obj, time=frame), joint_mat)
    joint_transform_mat = om.MTransformationMatrix(joint_mat)

    euler_rot = joint_transform_mat.eulerRotation()
    euler_rot.reorderIt(rot_order)
    translation = joint_transform_mat.getTranslation(om.MSpace.kTransform)
    angles = [math.degrees(angle) for angle in (euler_rot.x, euler_rot.y, euler_rot.z)]
    frame_dict = {
        'tx': "%.8f" % translation.x,
        'ty': "%.8f" % translation.y,
        'tz': "%.8f" % translation.z,
        'rx': "%.8f" % (angles[0]),
        'ry': "%.8f" % (angles[1]),
        'rz': "%.8f" % (angles[2])
    }
    return frame_dict

#root joints pass values from world space
def _get_frame_dist_for_root(obj, frame):
    # get world matrix for root joint
    root_joint_world_matrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(cmds.getAttr('%s.worldMatrix' % obj, time=frame), root_joint_world_matrix)
    joint_world_matrix = om.MTransformationMatrix(root_joint_world_matrix)

    # read rotation in world space
    rot_order = cmds.getAttr('%s.rotateOrder' % obj)
    euler_rot = joint_world_matrix.eulerRotation()
    euler_rot.reorderIt(rot_order)
    translation = joint_world_matrix.getTranslation(om.MSpace.kWorld)
    angles = [math.degrees(angle) for angle in (euler_rot.x, euler_rot.y, euler_rot.z)]
    frame_dict = {
        'tx': "%.8f" % translation.x,
        'ty': "%.8f" % translation.y,
        'tz': "%.8f" % translation.z,
        'rx': "%.8f" % (angles[0]),
        'ry': "%.8f" % (angles[1]),
        'rz': "%.8f" % (angles[2])
    }
    return frame_dict

def _export_json(json_object, file_name):
    if ".json" not in file_name:
        file_name += ".json"
    complete_name = os.path.join(os.path.expanduser('~'))
    complete_name += "/" + file_name

    with open(complete_name, "w") as jsonFile:
        json.dump(json_object, jsonFile, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ':'))
    print("Finished writing data to {0}".format(complete_name))

