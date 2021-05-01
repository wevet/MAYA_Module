# coding: utf-8
import maya.cmds as cmds
import random

"""
using

import example
import importlib
importlib.reload(example)
example.create_hat()


"""


def create_hat(cone_color=None, pompom_color=None):
    cone_obj, cone_node = cmds.polyCone()
    pompom_obj, pompom_node = cmds.polySphere(r=0.25)
    cmds.move(0, 1.06, 0)

    change_color(cone_obj, 'blinn', cone_color)
    change_color(pompom_obj, 'lambert', pompom_color)
    cmds.polyUnite(cone_obj, pompom_obj, n='hat')


def change_color(object, material, color):
    cmds.sets(name=material + 'MaterialGroup', renderable=True, empty=True)
    cmds.shadingNode(material, name=material + 'Shader', asShader=True)

    if not color:
        red = random.random()
        green = random.random()
        blue = random.random()
        cmds.setAttr(material + 'Shader.color', red, green, blue, type='double3')
    else:
        red = color[0]
        green = color[1]
        blue = color[2]
        cmds.setAttr(material + 'Shader.color', red, green, blue, type='double3')

    cmds.surfaceShaderList(material + 'Shader', add=material + 'MaterialGroup')
    cmds.sets(object, e=True, forceElement=material + 'MaterialGroup')


