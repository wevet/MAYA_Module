# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
import animtion_utilities as util

"""
usage 
import copy_animation
import importlib
importlib.reload(copy_animation)
copy_animation.show_ui()
"""

# Description
# Copy animation curves either completely or in part from one node or hierarchy
# to another.
#
# Usage
# Select the source and destination node (or top node) and press the button to
# either copy the selected node only, or the whole hierarchy underneath. Highlight
# the timeline if you want to copy just that part of the animation. Use the Copy
# to New Layer option if you want the curves copied into a new animation layer, in
# order to preserve the original animation, or to blend.
#
# Ui
# [] Copy To New Layer : Create a new animation layer to copy the curves into, preserving the original animation.
# [Copy Single] : Copy animation from one object to another (or multiple).
# [Copy Hierarchy] : Uses name matching to copy animation across hierarchies.
#


def show_ui():
    with util.MlUi('copy_animation', 'Copy Animation', width=400, height=120, info='''Copy animation across single nodes, or hierarchies based on name. You can copy to multiple destinations at once using Copy Single. Highlight the timeline to copy just that part of the animation.''') as win:
        mc.checkBoxGrp('copy_animation_layer_checkBox', label='Copy To New Layer',
                       annotation='Create a new animation layer to copy the curves into, preserving the original animation.')
        win.ButtonWithPopup(label='Copy Single', command=copy_single_animation,
                            annotation='Copy animation from one object to another (or multiple).', shelfLabel='cpAn',
                            shelfIcon='defaultTwoStackedLayout',
                            readUI_toArgs={'addToLayer': 'copy_animation_layer_checkBox'})
        win.ButtonWithPopup(label='Copy Hierarchy', command=copy_hierarchy,
                            annotation='Uses name matching to copy animation across hierarchies.', shelfLabel='cpAn',
                            shelfIcon='defaultTwoStackedLayout',
                            readUI_toArgs={'addToLayer': 'copy_animation_layer_checkBox'})


def _get_start_and_end():
    """
    フレーム範囲がハイライトされている場合のみ、開始と終了を返す。そうでない場合は、利用可能なすべてのアニメーションを使用
    """
    gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
    if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
        start, end = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
        return start, end - 1
    return None, None

def copy_single_animation(source=None, destination=None, pasteMethod='replace', offset=0, addToLayer=False, rotateOrder=True):
    """
    ソースノードからアニメーションをコピーし、デスティネーションノードにペースト
    """
    start, end = _get_start_and_end()
    if not source and not destination:
        sel = mc.ls(sl=True)
        if len(sel) < 2:
            OpenMaya.MGlobal.displayWarning('Please select 2 or more objects.')
            return
        source = sel[0]
        destination = sel[1:]
    layer = None
    if addToLayer:
        layer = util.createAnimLayer(destination, namePrefix='ml_cp')
    do_copy_animation(source=source, destination=destination, pasteMethod=pasteMethod, offset=offset, start=start, end=end, layer=layer, rotateOrder=rotateOrder)

def copy_hierarchy(sourceTop=None, destinationTop=None, pasteMethod='replace', offset=0, addToLayer=False, layerName=None, rotateOrder=True):
    """
    ソース階層からアニメーションをコピーし、デスティネーション階層にペーストすることができる。
    """
    start, end = _get_start_and_end()

    if not sourceTop and not destinationTop:
        sel = mc.ls(sl=True)
        if len(sel) != 2:
            OpenMaya.MGlobal.displayWarning('Please select exactly 2 objects.')
            return
        sourceTop = sel[0]
        destinationTop = sel[1]
    # get keyed objects below source
    nodes = mc.listRelatives(sourceTop, pa=True, ad=True) or []
    nodes.append(sourceTop)
    keyed = []

    for node in nodes:
        # this will only return time based keyframes, not driven keys
        if mc.keyframe(node, time=(':',), query=True, keyframeCount=True):
            keyed.append(node)
    if not keyed:
        return
    # get a list of all nodes under the destination
    all_dest_nodes = mc.listRelatives(destinationTop, ad=True, pa=True) or []
    all_dest_nodes.append(destinationTop)

    dest_node_map = {}
    duplicate = []
    for each in all_dest_nodes:
        name = each.rsplit('|')[-1].rsplit(':')[-1]
        if name in duplicate:
            continue
        if name in list(dest_node_map.keys()):
            duplicate.append(name)
            continue
        dest_node_map[name] = each
    destNS = util.getNamespace(destinationTop)
    layer = None
    if addToLayer:
        if not layerName:
            layerName = 'copyHierarchy'
        layer = util.createAnimLayer(name=layerName)
    for node in keyed:
        # strip name
        nodeName = node.rsplit('|')[-1].rsplit(':')[-1]
        if nodeName in duplicate:
            print('2つ以上のデスティネーションノードが同じ名前です: ' + destNS + nodeName)
            continue
        if nodeName not in list(dest_node_map.keys()):
            print('デスティネーションノードが見つかりません: ' + destNS + nodeName)
            continue
        do_copy_animation(source=node, destination=dest_node_map[nodeName], pasteMethod=pasteMethod, offset=offset, start=start, end=end, layer=layer, rotateOrder=rotateOrder)

def do_copy_animation(source=None, destination=None, pasteMethod='replace', offset=0, start=None, end=None, layer=None, rotateOrder=True):
    """
    Actually do the copy and paste from one node to another. If start and end frame is specified,
    set a temporary key before copying, and delete it afterward.
    """

    if not isinstance(destination, (list, tuple)):
        destination = [destination]

    if layer:
        mc.select(destination)
        mc.animLayer(layer, edit=True, addSelectedObjects=True)

        # we want to make sure rotation values are within 360 degrees, so we don't get flipping when blending layers.
        util.minimizeRotationCurves(source)
        for each in destination:
            util.minimizeRotationCurves(each)

    if rotateOrder:
        for each in destination:
            try:
                if mc.getAttr(each + '.rotateOrder', keyable=True):
                    mc.setAttr(each + '.rotateOrder', mc.getAttr(source + '.rotateOrder'))
            except ZeroDivisionError:
                pass

    if pasteMethod == 'replaceCompletely' or not start or not end:
        mc.copyKey(source)
        if layer:
            mc.animLayer(layer, edit=True, selected=True)
        for each in destination:
            mc.pasteKey(each, option=pasteMethod, timeOffset=offset)
    else:

        # need to do this per animation curve, unfortunately, to make sure we're not adding or removing too many keys
        animCurves = mc.keyframe(source, query=True, name=True)
        if not animCurves:
            return

        # story cut key times as 2 separate lists means we only have to run 2 cutkey commands, rather than looping through each
        cutStart = []
        cutEnd = []
        for curve in animCurves:

            # does it have keyframes on the start and end frames?
            startKey = mc.keyframe(curve, time=(start,), query=True, timeChange=True)
            endKey = mc.keyframe(curve, time=(end,), query=True, timeChange=True)

            # if it doesn't set a temporary key for start and end
            # and store the curve name in the appropriate list
            if not startKey:
                mc.setKeyframe(curve, time=(start,), insert=True)
                cutStart.append(curve)
            if not endKey:
                mc.setKeyframe(curve, time=(end,), insert=True)
                cutEnd.append(curve)

        mc.copyKey(source, time=(start, end))
        if layer:
            for each in mc.ls(type='animLayer'):
                mc.animLayer(each, edit=True, selected=False, preferred=False)
            mc.animLayer(layer, edit=True, selected=True, preferred=True)
        for each in destination:
            mc.pasteKey(each, option=pasteMethod, time=(start, end), copies=1, connect=0, timeOffset=offset)

        # if we set temporary source keys, delete them now
        if cutStart:
            mc.cutKey(cutStart, time=(start,))
        if cutEnd:
            mc.cutKey(cutEnd, time=(end,))

def marking_menu():
    """
    Example of how a marking menu could be set up.
    """
    menuKwargs = {'enable': True, 'subMenu': False, 'enableCommandRepeat': True, 'optionBox': False, 'boldFont': True}
    mc.menuItem(radialPosition='E', label='Copy Hierarchy', command=copy_hierarchy, **menuKwargs)
    mc.menuItem(radialPosition='W', label='Copy Single', command=copy_single_animation, **menuKwargs)
    mc.menuItem(label='Copy Anim UI', command=show_ui, **menuKwargs)


