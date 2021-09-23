# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
from functools import partial

kMainWindowName = 'Chain Window'

"""
import chain_rig
import importlib
importlib.reload(chain_rig)
chain_rig.create_main_window()
"""


def create_main_window():
    if cmds.window(kMainWindowName, exists=1):
        cmds.deleteUI(kMainWindowName)
    window = cmds.window(kMainWindowName, title='ChainRig', sizeable=1)

    # Create form + UI elements
    form = cmds.formLayout(numberOfDivisions=100)
    scroll = cmds.scrollLayout(parent=form)
    scroll_form = cmds.formLayout(numberOfDivisions=100, parent=scroll)

    start_joint_text = cmds.textFieldGrp(label='Start Joint: ', adjustableColumn=2, editable=0)
    start_joint_btn = cmds.button(label='Set Selected', command=partial(check_selected_joint, start_joint_text))

    end_joint_text = cmds.textFieldGrp(label='End Joint: ', adjustableColumn=2, editable=0)
    endJointBtn = cmds.button(label='Set Selected', command=partial(check_selected_joint, end_joint_text))

    bone_int_slider = cmds.intSliderGrp(label='Number of Bones: ',
                                      field=1, step=2,
                                      minValue=2, maxValue=100, value=10,
                                      adjustableColumn=3)

    joint_chain_options = cmds.optionMenuGrp(label='Joint Chain: ',
                                             changeCommand=partial(change_joint_chain, bone_int_slider))
    cmds.menuItem(label='Create From Start/End Joints')
    cmds.menuItem(label='Use Existing Joint Chain')

    control_int_slider = cmds.intSliderGrp(label='Number of Controls: ', field=1, step=2,
                                         minValue=2, maxValue=30, value=4, adjustableColumn=3)
    start_color_slider = cmds.colorSliderGrp(label='Start Control Color: ', rgb=(0, 0, 1))
    end_color_slider = cmds.colorSliderGrp(label='End Control Color: ', rgb=(0, 1, 0))
    volume_preserve_checkbox = cmds.checkBoxGrp(label='Preserve Volume: ', visible=0)

    spline_type_options = cmds.optionMenuGrp(label='Spline Type: ',
                                           changeCommand=partial(change_spline_type,
                                                                 control_int_slider,
                                                                 start_color_slider,
                                                                 end_color_slider,
                                                                 volume_preserve_checkbox))
    cmds.menuItem(label='Cluster Controls')
    cmds.menuItem(label='Stretchy Spine')

    chain_btn = cmds.button(label='Create Chain !',
                            command=partial(execute_chain,
                                            joint_chain_options, start_joint_text, end_joint_text, bone_int_slider,
                                            spline_type_options, control_int_slider, start_color_slider, end_color_slider,
                                            volume_preserve_checkbox),
                            parent=form)

    apply_btn = cmds.button(label='Apply',
                           command=partial(apply_chain,
                                           joint_chain_options, start_joint_text, end_joint_text, bone_int_slider,
                                           spline_type_options, control_int_slider, start_color_slider, end_color_slider,
                                           volume_preserve_checkbox),
                           parent=form)

    close_btn = cmds.button(label='Close', command=partial(close_window), parent=form)

    # Format UI elements
    cmds.formLayout(form, edit=1,
                    attachForm=[
                        (scroll, 'top', 5), (scroll, 'left', 5), (scroll, 'right', 5),
                        (chain_btn, 'left', 5), (chain_btn, 'bottom', 5),
                        (apply_btn, 'bottom', 5),
                        (close_btn, 'bottom', 5), (close_btn, 'right', 5)],
                    attachControl=[
                        (scroll, 'bottom', 5, chain_btn),
                        (chain_btn, 'right', 5, apply_btn),
                        (close_btn, 'left', 5, apply_btn), ],
                    attachPosition=[(apply_btn, 'left', 0, 34), (apply_btn, 'right', 0, 66), ]
                    )

    cmds.formLayout(scroll_form, edit=1,
                    attachForm=[
                        (joint_chain_options, 'top', 25), (joint_chain_options, 'left', 0),
                        (start_joint_text, 'left', 0), (start_joint_btn, 'right', 10),

                        (end_joint_text, 'left', 0),
                        (end_joint_text, 'right', 0),
                        (endJointBtn, 'right', 10),

                        (bone_int_slider, 'left', 0), (bone_int_slider, 'right', 0),

                        (spline_type_options, 'left', 0),

                        (control_int_slider, 'left', 0), (control_int_slider, 'right', 0),
                        (start_color_slider, 'left', 0), (start_color_slider, 'right', 0),
                        (end_color_slider, 'left', 0), (end_color_slider, 'right', 0),
                        (volume_preserve_checkbox, 'left', 0),
                        (volume_preserve_checkbox, 'right', 0),
                        (volume_preserve_checkbox, 'bottom', 5),
                    ],
                    attachControl=[
                        (joint_chain_options, 'bottom', 5, start_joint_text),
                        (start_joint_text, 'bottom', 5, end_joint_text),
                        (start_joint_text, 'right', 5, start_joint_btn),
                        (start_joint_btn, 'bottom', 5, endJointBtn),
                        (end_joint_text, 'right', 5, endJointBtn),
                        (end_joint_text, 'bottom', 5, bone_int_slider),
                        (endJointBtn, 'bottom', 5, bone_int_slider),
                        (bone_int_slider, 'bottom', 5, spline_type_options),
                        (spline_type_options, 'bottom', 5, control_int_slider),
                        (control_int_slider, 'bottom', 5, start_color_slider),
                        (start_color_slider, 'bottom', 5, end_color_slider),
                        (end_color_slider, 'bottom', 5, volume_preserve_checkbox),
                    ]
                    )
    cmds.showWindow(window)


def close_window(*args):
    cmds.deleteUI(kMainWindowName)


def check_selected_joint(joint_text, *args):
    ik_control = cmds.ls(selection=1)
    if len(ik_control) != 1:
        cmds.confirmDialog(title='Error', message='Please select a joint.')
        return False
    elif cmds.objectType(ik_control) != 'joint':
        cmds.confirmDialog(title='Error', message='Object selected is not a joint.')
    else:
        cmds.textFieldGrp(joint_text, edit=1, text=cmds.ls(selection=1)[0])


def change_joint_chain(bone_int_slider, *args):
    if args[0] == 'Create From Start/End Joints':
        cmds.intSliderGrp(bone_int_slider, edit=1, visible=1)
    elif args[0] == 'Use Existing Joint Chain':
        cmds.intSliderGrp(bone_int_slider, edit=1, visible=0)


def change_spline_type(control_int_slider, start_color_slider, end_color_slider, volume_preserve_checkbox, *args):
    if args[0] == 'Cluster Controls':
        cmds.intSliderGrp(control_int_slider, edit=1, visible=1)
        cmds.colorSliderGrp(start_color_slider, edit=1, visible=1)
        cmds.colorSliderGrp(end_color_slider, edit=1, visible=1)
        cmds.checkBoxGrp(volume_preserve_checkbox, edit=1, visible=0)
    elif args[0] == 'Stretchy Spine':
        cmds.intSliderGrp(control_int_slider, edit=1, visible=0)
        cmds.colorSliderGrp(start_color_slider, edit=1, visible=0)
        cmds.colorSliderGrp(end_color_slider, edit=1, visible=0)
        cmds.checkBoxGrp(volume_preserve_checkbox, edit=1, visible=1)


def execute_chain(joint_chain_options, start_joint_text, end_joint_text, bone_int_slider, spline_type_options,
                  control_int_slider,
                  start_color_slider, end_color_slider, volume_preserve_checkbox, *args):

    apply_chain(joint_chain_options, start_joint_text, end_joint_text, bone_int_slider,
                spline_type_options, control_int_slider,
                start_color_slider, end_color_slider, volume_preserve_checkbox)
    close_window()


def apply_chain(joint_chain_options, start_joint_text, end_joint_text, bone_int_slider, spline_type_options,
                control_int_slider,
                start_color_slider, end_color_slider, volume_preserve_checkbox, *args):

    joint_chain_option = cmds.optionMenuGrp(joint_chain_options, q=1, value=1)
    start_joint = cmds.textFieldGrp(start_joint_text, q=1, text=1)
    end_joint = cmds.textFieldGrp(end_joint_text, q=1, text=1)
    bone_count = cmds.intSliderGrp(bone_int_slider, q=1, value=1)
    spline_type_option = cmds.optionMenuGrp(spline_type_options, q=1, value=1)
    control_count = cmds.intSliderGrp(control_int_slider, q=1, value=1)
    start_color = cmds.colorSliderGrp(start_color_slider, q=1, rgbValue=1)
    end_color = cmds.colorSliderGrp(end_color_slider, q=1, rgbValue=1)
    preserve_volume = cmds.checkBoxGrp(volume_preserve_checkbox, q=1, value1=1)

    if start_joint == '' or end_joint == '':
        cmds.confirmDialog(title='Error', message="Please fill in all text fields.")
        return
    if start_joint == end_joint:
        cmds.confirmDialog(title='Error', message="Start and end joints are identical.")
        return

    create_spline(joint_chain_option, start_joint, end_joint, bone_count,
                  spline_type_option, control_count,
                  start_color, end_color, preserve_volume)


def create_spline(joint_chain_option, start_joint, end_joint, bone_num,
                  spline_type_option, handle_num,
                  start_color, end_color, preserve_volume):
    joint_chain = None
    naming_prefix = None

    if joint_chain_option == 'Create From Start/End Joints':
        joint_chain = create_joint_chain(start_joint, end_joint, bone_num)
    elif joint_chain_option == 'Use Existing Joint Chain':
        joint_chain = get_joint_chain(start_joint, end_joint)

    spline_ik_handle, spline_curve = create_spline_ik(joint_chain, handle_num)

    if spline_type_option == 'Cluster Controls':
        lengthCtrl = create_length_control(joint_chain, start_joint)
        clusters, cluster_controls = cluster_curve(spline_curve)

        if joint_chain_option == 'Create From Start/End Joints':
            re_connect_joints(start_joint, end_joint, joint_chain, clusters)

        group_all(spline_ik_handle, spline_curve, clusters, cluster_controls, lengthCtrl)
        re_color_control(start_color, end_color, cluster_controls)

    elif spline_type_option == 'Stretchy Spine':
        start_bind_joint, end_bind_joint, start_bind_control, end_bind_control = create_bind_joints(start_joint, end_joint, spline_curve)
        make_stretchy(spline_curve, joint_chain, preserve_volume)
        cmds.group(spline_ik_handle, spline_curve, start_bind_joint, end_bind_joint, start_bind_control, end_bind_control, name='str_all_GRP')


def create_joint_chain(start_joint, end_joint, bone_num):
    joint_chain = []
    cmds.select(clear=1)

    # Get distance between start and end joints
    start_pos = cmds.xform(start_joint, q=1, rotatePivot=1, worldSpace=1)
    end_pos = cmds.xform(end_joint, q=1, rotatePivot=1, worldSpace=1)

    dist = [
        end_pos[0] - start_pos[0],
        end_pos[1] - start_pos[1],
        end_pos[2] - start_pos[2]
    ]

    for i in range(bone_num):
        # Create bone at position
        new_position = [
            start_pos[0] + (float(i) / bone_num) * dist[0],
            start_pos[1] + (float(i) / bone_num) * dist[1],
            start_pos[2] + (float(i) / bone_num) * dist[2]
        ]
        bone = cmds.joint(position=new_position, name='spl_%s_J' % i, radius=cmds.joint(start_joint, q=1, radius=1)[0])

        # Orient previous bone to newly created bone
        if i >= 1:
            previous_bone = joint_chain[len(joint_chain) - 1]
            cmds.joint(previous_bone, edit=1, orientJoint='xyz', secondaryAxisOrient='yup')
        joint_chain.append(bone)

    # Create end bone
    bone = cmds.joint(position=end_pos, name='spl_%s_J' % bone_num)
    previous_bone = joint_chain[len(joint_chain) - 1]
    orient = cmds.joint(previous_bone, q=1, orientation=1)
    cmds.joint(bone, edit=1, orientation=orient, radius=cmds.joint(start_joint, q=1, radius=1)[0])
    joint_chain.append(bone)
    return joint_chain


def get_joint_chain(start_joint, end_joint):
    joint_chain = [end_joint]
    parent_joint = cmds.listRelatives(end_joint, parent=1)[0]
    while parent_joint != start_joint:
        joint_chain.append(parent_joint)
        parent_joint = cmds.listRelatives(parent_joint, parent=1)[0]
    joint_chain.append(start_joint)
    joint_chain.reverse()
    return joint_chain


def create_spline_ik(joint_chain, handle_num):
    spline_ik = cmds.ikHandle(solver='ikSplineSolver', startJoint=joint_chain[0],
                             endEffector=joint_chain[len(joint_chain) - 1],
                             name='spl_spline_IK_#', numSpans=handle_num - 2)
    spline_ik_handle = spline_ik[0]
    spline_curve = spline_ik[2]
    spline_curve = cmds.rename(spline_curve, 'spl_spline_CRV_#')
    return spline_ik_handle, spline_curve


def create_length_control(joint_chain, start_joint):
    start_joint_pos = cmds.xform(start_joint, q=1, translation=1, worldSpace=1)
    length_control = create_cube_control('spl_length_CTRL', start_joint_pos)
    cmds.scale(2, 2, 2, length_control)
    cmds.addAttr(longName='length', keyable=1, defaultValue=1.0, minValue=0.0)
    cmds.setAttr(length_control + '.translateX', lock=1, keyable=False)
    cmds.setAttr(length_control + '.translateY', lock=1, keyable=False)
    cmds.setAttr(length_control + '.translateZ', lock=1, keyable=False)
    cmds.setAttr(length_control + '.rotateX', lock=1, keyable=False)
    cmds.setAttr(length_control + '.rotateY', lock=1, keyable=False)
    cmds.setAttr(length_control + '.rotateZ', lock=1, keyable=False)
    cmds.setAttr(length_control + '.scaleX', lock=1, keyable=False)
    cmds.setAttr(length_control + '.scaleY', lock=1, keyable=False)
    cmds.setAttr(length_control + '.scaleZ', lock=1, keyable=False)

    # Scale every bone's length by this multiplier
    for bone in joint_chain:
        cmds.connectAttr(length_control + '.length', bone + '.scaleX')

    return length_control


def cluster_curve(spline_curve):
    clusters = []
    cluster_controls = []

    # Get all CVs in spline curve
    curveCVs = cmds.ls('%s.cv[:]' % spline_curve, flatten=1)

    for i, cv in enumerate(curveCVs):
        # Create cluster for each CV
        curve_cluster = cmds.cluster(cv, name='spl_%s_CL' % i)
        curve_cluster = curve_cluster[1]  # cmds.cluster() returns [cluster, handle]
        clusters.append(curve_cluster)

        if i > 0:
            # Create control for cluster
            cv_pos = cmds.pointPosition(cv)
            cv_control = create_cube_control('spl_%s_CTRL' % i, cv_pos)
            cmds.makeIdentity(cv_control, apply=1, t=1, r=1, s=1, n=0)
            cmds.parentConstraint(cv_control, curve_cluster, maintainOffset=1)
            cluster_controls.append(cv_control)
    return clusters, cluster_controls


def re_connect_joints(start_joint, end_joint, joint_chain, clusters):
    cmds.pointConstraint(start_joint, clusters[0], maintainOffset=1)
    # Unparent end joint, point constrain to spline IK handle
    cmds.parent(end_joint, world=1)
    cmds.pointConstraint(joint_chain[len(joint_chain) - 1], end_joint, maintainOffset=1)


def group_all(spline_ik_handle, spline_curve, clusters, cluster_controls, length_control):
    # Group clusters and controls
    cluster_grp = group('spl_clusters_GRP', clusters)
    control_group = group('spl_ctrls_GRP', cluster_controls)
    cluster_controls.insert(0, length_control)
    cmds.parent(length_control, control_group)
    # Group spline data (IK handle + curve)
    splineGrp = cmds.group(spline_ik_handle, spline_curve, name='spl_spline_GRP')
    # Group clusters, controls and spline data into master group
    masterGrp = cmds.group(cluster_grp, control_group, splineGrp, name='spl_all_GRP')


def group(group_name, object_list):
    grp = cmds.group(empty=1, name=group_name)
    for obj in object_list:
        cmds.parent(obj, grp)
    return grp


def create_cube_control(cube_name, pos):
    cube = cmds.curve(
        degree=1,
        point=(
            (1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1),
            (1, 1, 1), (1, -1, 1), (1, -1, -1), (1, 1, -1),
            (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, -1, -1),
            (-1, -1, 1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1)
        ),
        name=cube_name
    )
    cmds.move(pos[0], pos[1], pos[2], cube, absolute=1)
    return cube


def re_color_control(start_color, end_color, control):
    color_diff = [
        end_color[0] - start_color[0],
        end_color[1] - start_color[1],
        end_color[2] - start_color[2]
    ]
    num_control = len(control)

    for i, ctrl in enumerate(control):
        color = [
            start_color[0] + (float(i) / (num_control - 1)) * color_diff[0],
            start_color[1] + (float(i) / (num_control - 1)) * color_diff[1],
            start_color[2] + (float(i) / (num_control - 1)) * color_diff[2]
        ]
        cmds.color(ctrl, rgbColor=color)


def create_bind_joints(startJoint, endJoint, splineCurve):
    start_bind_joint, start_bind_control = create_bind_joint(startJoint)
    end_bind_joint, end_bind_control = create_bind_joint(endJoint)
    # classic linear skinning
    cmds.skinCluster(start_bind_joint, end_bind_joint, splineCurve, toSelectedBones=True, skinMethod=0, normalizeWeights=1)
    return start_bind_joint, end_bind_joint, start_bind_control, end_bind_control


def create_bind_joint(joint):
    bind_joint = cmds.duplicate(joint, parentOnly=1, n=joint.replace('_J', '_bind_J'))
    bind_joint_pos = cmds.xform(joint, q=1, rotatePivot=1, worldSpace=1)
    bind_control = create_cube_control(joint.replace('_J', '_bind_CTRL'), bind_joint_pos)
    cmds.makeIdentity(bind_control, apply=1, t=1, r=1, s=1, n=0)
    cmds.parentConstraint(bind_control, bind_joint, maintainOffset=1)
    bind_joint_parent = cmds.listRelatives(bind_joint, parent=1)
    if bind_joint_parent is not None and bind_joint_parent[0] != 'world':
        cmds.parent(bind_joint, world=1)
    return bind_joint, bind_control


def make_stretchy(curve, joint_chain, preserve_volume):
    # Create curveInfo node to get arclength
    curve_info = cmds.arclen(curve, constructionHistory=1)
    curve_info = cmds.rename(curve_info, curve + 'Info')

    # Create division node
    arclenDiv = curve_info.replace('Info', '_arclen_MD')
    arclenDiv = cmds.createNode('multiplyDivide', name=arclenDiv)
    cmds.setAttr(arclenDiv + '.operation', 2)  # divide

    # Divide curve's current arclength by base arclength,
    # to get a multiplier for bone length
    cmds.connectAttr(curve_info + '.arcLength', arclenDiv + '.input1X')
    baseArclen = cmds.getAttr(arclenDiv + '.input1X')
    cmds.setAttr(arclenDiv + '.input2X', baseArclen)

    power_div = None
    if preserve_volume:
        power_div = curve_info.replace('Info', '_power_MD')
        power_div = cmds.createNode('multiplyDivide', name=power_div)
        cmds.setAttr(power_div + '.operation', 3)  # power
        cmds.connectAttr(arclenDiv + '.outputX', power_div + '.input1X')
        cmds.setAttr(power_div + '.input2X', -0.5)

    for joint in joint_chain:
        cmds.connectAttr(arclenDiv + '.outputX', joint + '.scaleX')
        if preserve_volume:
            cmds.connectAttr(power_div + '.outputX', joint + '.scaleY')
            cmds.connectAttr(power_div + '.outputX', joint + '.scaleZ')


