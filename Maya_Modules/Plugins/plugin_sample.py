# -*- coding: utf-8 -*-
import sys
import maya.api.OpenMaya as OpenMaya

# プラグインの名前
kPluginCmdName = 'PluginSample'


"""
import maya.cmds as cmds
cmds.loadPlugin("plugin_sample.py")
cmds.PluginSample()
"""


class PluginSample(OpenMaya.MPxCommand):

    def __init__(self):
        OpenMaya.MPxCommand.__init__(self)

    def doIt(self, args):
        print("Hello, PluginSample!")
        pass


def cmdCreator():
    return PluginSample()


def initializePlugin(mObject):
    mPlugin = OpenMaya.MFnPlugin(mObject)
    try:
        mPlugin.registerCommand(kPluginCmdName, cmdCreator)
    except ArithmeticError as e:
        sys.stderr.write('Failed to register command: ' + kPluginCmdName)
        raise


def uninitializePlugin(mObject):
    mPlugin = OpenMaya.MFnPlugin(mObject)
    try:
        mPlugin.deregisterCommand(kPluginCmdName)
    except ArithmeticError as e:
        sys.stderr.write('Failed to unregister command: ' + kPluginCmdName)
        raise

