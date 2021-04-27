# conding: utf-8
import maya.cmds as cmds


"""
using 

import joint_size as joint
joint.set_joint_size_GUI()
"""


# jointのみradiusを一括変換
def set_joint_size(*args):

    if not cmds.ls(sl=True):
        print("Nothing is selected")
    else:
        first_selected = cmds.ls(sl=True)[0]

        try:
            joint_size = float(cmds.textFieldButtonGrp('Set_JointSize_Button',query=True, text=True))
            cmds.select(hierarchy=True)
            selected_object = cmds.ls(sl=True)
            for node in selected_object:
                if cmds.objectType( node ) != 'joint':
                    print("Not jointType" + cmds.objectType(node))
                    continue
                cmds.setAttr( node + '.radius', joint_size)

            cmds.select(clear=True)
            cmds.select(first_selected, replace=True)

        except:
            print("Please Input Radius Size")



# jointSizeを調整するGUI
def set_joint_size_GUI():
    if cmds.window("SetJointSize", exists=True):
        cmds.deleteUI("SetJointSize")

    window = cmds.window('SetJointSize', title='Set Joint Size', sizeable=False, topLeftCorner=[200, 200], widthHeight=(320, 120))
    cmds.columnLayout()
    cmds.rowLayout(numberOfColumns=2)
    cmds.textFieldButtonGrp('Set_JointSize_Button',label='Set Joint Size', text='0.5', buttonLabel='Set Size', columnWidth3=[80,50,70], buttonCommand=set_joint_size)
    cmds.button(label='Close', command='cmds.deleteUI("SetJointSize")')
    cmds.showWindow(window)
    



