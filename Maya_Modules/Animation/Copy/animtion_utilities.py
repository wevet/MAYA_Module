# -*- coding: utf-8 -*-


__revision__ = 1

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
from functools import partial
import shutil, os, re, sys, math

# declare some variables
TOOL_URL = 'tool/'
ICON_URL = 'icons/'
GITHUB_ROOT_URL = ''

# try to add to the icon path if there is an icons folder in this directory
THIS_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(THIS_DIR, 'icons').replace('\\', '/')
if os.path.isdir(ICON_PATH) and ICON_PATH not in os.environ['XBMLANGPATH']:
    os.environ['XBMLANGPATH'] = os.pathsep.join((os.environ['XBMLANGPATH'], ICON_PATH))
MAYA_VERSION = mm.eval('getApplicationVersionAsFloat')

def _show_help_command(url):
    """
    This just returns the maya command for launching a web page, since that gets called a few times
    """
    return 'import maya.cmds;maya.cmds.showHelp("' + url + '",absolute=True)'

def castToTime(time):
    """
    Maya's keyframe commands are finnicky about how lists of times or indicies are formatted.
    """
    if isinstance(time, (list, tuple)):
        return [(x,) for x in time]
    return (time,)

def constrain(source, destination, translate=True, rotate=True, scale=False, maintainOffset=False):
    """
    Constrain two objects, even if they have some locked attributes.
    """
    transAttr = None
    rotAttr = None
    scaleAttr = None
    if translate:
        transAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='translate*')
    if rotate:
        rotAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='rotate*')
    if scale:
        scaleAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='scale*')

    rotSkip = list()
    transSkip = list()

    for axis in ['x', 'y', 'z']:
        if transAttr and not 'translate' + axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate' + axis.upper() in rotAttr:
            rotSkip.append(axis)
    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'
    constraints = list()
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(mc.parentConstraint(source, destination, maintainOffset=maintainOffset))
    else:
        if transAttr:
            constraints.append(mc.pointConstraint(source, destination, skip=transSkip, maintainOffset=maintainOffset))
        if rotAttr:
            constraints.append(mc.orientConstraint(source, destination, skip=rotSkip, maintainOffset=maintainOffset))
    return constraints


def create_animation_layer(nodes=None, name=None, namePrefix='', override=True):
    # if there's no layer name, generate one
    if not name:
        if namePrefix:
            namePrefix += '_'
        if nodes:
            shortNodes = mc.ls(nodes, shortNames=True)
            shortNodes = [x.rpartition(':')[-1] for x in shortNodes]
            # if there's just one node, use it's name minus the namespace
            if len(shortNodes) == 1:
                name = namePrefix + shortNodes[0]
            else:
                # try to find the longest common substring
                commonString = longest_common_substring(shortNodes)
                if commonString:
                    name = commonString
                elif ':' in nodes[0]:
                    # otherwise use the namespace if it has one
                    name = nodes[0].rpartition(':')[-1]
        if not name:
            if not namePrefix:
                namePrefix = 'ml_'
            name = namePrefix + 'animLayer'

    layer = mc.animLayer(name, override=override)

    # add the nodes to the layer
    if nodes:
        sel = mc.ls(sl=True)
        mc.select(nodes)
        mc.animLayer(layer, edit=True, addSelectedObjects=True)
        if sel:
            mc.select(sel)
        else:
            mc.select(clear=True)

    # select the layer
    select_animation_layer(layer)
    return layer

def select_animation_layer(animLayer=None):
    # deselect all layers
    for each in mc.ls(type='animLayer'):
        mc.animLayer(each, edit=True, selected=False, preferred=False)
    if animLayer:
        mc.animLayer(animLayer, edit=True, selected=True, preferred=True)

def get_selected_animation_layers():
    layers = list()
    for each in mc.ls(type='animLayer'):
        if mc.animLayer(each, query=True, selected=True):
            layers.append(each)
    return layers

def createHotkey(command, name, description='', python=True):
    """
    Open up the hotkey editor to create a hotkey from the specified command
    """

    if MAYA_VERSION > 2015:
        print("Creating hotkeys currently doesn't work in the new hotkey editor.")
        print("Here's the command, you'll have to make the hotkey yourself (sorry):")
        print(command)
        OpenMaya.MGlobal.displayWarning("Couldn't create hotkey, please see script editor for details...")
        return

    mm.eval('hotkeyEditor')
    mc.textScrollList('HotkeyEditorCategoryTextScrollList', edit=True, selectItem='User')
    mm.eval('hotkeyEditorCategoryTextScrollListSelect')
    mm.eval('hotkeyEditorCreateCommand')

    mc.textField('HotkeyEditorNameField', edit=True, text=name)
    mc.textField('HotkeyEditorDescriptionField', edit=True, text=description)

    if python:
        if MAYA_VERSION < 2013:
            command = 'python("' + command + '");'
        else:  # 2013 or above
            mc.radioButtonGrp('HotkeyEditorLanguageRadioGrp', edit=True, select=2)

    mc.scrollField('HotkeyEditorCommandField', edit=True, text=command)


def createShelfButton(command, label='', name=None, description='', image=None, labelColor=(1, 0.5, 0), labelBackgroundColor=(0, 0, 0, 0.5), backgroundColor=None):
    """
    Create a shelf button for the command on the current shelf
    """
    # some good default icons:
    # menuIconConstraints - !
    # render_useBackground - circle
    # render_volumeShader - black dot
    # menuIconShow - eye

    gShelfTopLevel = mm.eval('$temp=$gShelfTopLevel')
    if not mc.tabLayout(gShelfTopLevel, exists=True):
        OpenMaya.MGlobal.displayWarning('Shelf not visible.')
        return

    if not name:
        name = label

    if not image:
        image = getIcon(name)
    if not image:
        image = 'render_useBackground'

    shelfTab = mc.shelfTabLayout(gShelfTopLevel, query=True, selectTab=True)
    shelfTab = gShelfTopLevel + '|' + shelfTab

    # add additional args depending on what version of maya we're in
    kwargs = {}
    if MAYA_VERSION >= 2009:
        kwargs['commandRepeatable'] = True
    if MAYA_VERSION >= 2011:
        kwargs['overlayLabelColor'] = labelColor
        kwargs['overlayLabelBackColor'] = labelBackgroundColor
        if backgroundColor:
            kwargs['enableBackground'] = bool(backgroundColor)
            kwargs['backgroundColor'] = backgroundColor

    return mc.shelfButton(parent=shelfTab, label=name, command=command,
                          imageOverlayLabel=label, image=image, annotation=description,
                          width=32, height=32, align='center', **kwargs)


def deselectChannels():
    """
    Deselect selected channels in the channelBox
    by clearing selection and then re-selecting
    """

    if not getSelectedChannels():
        return
    sel = mc.ls(sl=True)
    mc.select(clear=True)
    mc.evalDeferred(partial(mc.select, sel))


def formLayoutGrid(form, controls, offset=1):
    """
    Controls should be a list of lists, and this will arrange them in a grid
    """

    kwargs = {'edit': True, 'attachPosition': []}
    rowInc = 100 / len(controls)
    colInc = 100 / len(controls[0])
    position = {'left': 0, 'right': 100, 'top': 0, 'bottom': 100}

    for r, row in enumerate(controls):
        position['top'] = r * rowInc
        position['bottom'] = (r + 1) * rowInc
        for c, ctrl in enumerate(row):
            position['left'] = c * colInc
            position['right'] = (c + 1) * colInc
            for k in list(position.keys()):
                kwargs['attachPosition'].append((ctrl, k, offset, position[k]))

    mc.formLayout(form, **kwargs)


def frameRange(start=None, end=None):
    """
    Returns the frame range based on the highlighted timeslider,
    or otherwise the playback range.
    """

    if not start and not end:
        gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
        if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            frameRange = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            start = frameRange[0]
            end = frameRange[1] - 1
        else:
            start = mc.playbackOptions(query=True, min=True)
            end = mc.playbackOptions(query=True, max=True)

    return start, end


def getChannelFromAnimCurve(curve, plugs=True):
    """
    Finding the channel associated with a curve has gotten really complicated since animation layers.
    This is a recursive function which walks connections from a curve until an animated channel is found.
    """

    # we need to save the attribute for later.
    attr = ''
    if '.' in curve:
        curve, attr = curve.split('.')

    nodeType = mc.nodeType(curve)
    if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
        source = mc.listConnections(curve + '.output', source=False, plugs=plugs)
        if not source and nodeType == 'animBlendNodeAdditiveRotation':
            # if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            # get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            # if we're not returning plugs, then we wont have an attr suffix to use, so just use X.
            attrSuffix = 'X'
            if plugs:
                attrSuffix = attr[-1]

            source = mc.listConnections(curve + '.output' + attrSuffix, source=False, plugs=plugs)
        if source:
            nodeType = mc.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return getChannelFromAnimCurve(source[0], plugs=plugs)
            return source[0]


def getCurrentCamera():
    """
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel,
    """

    panel = mc.getPanel(withFocus=True)

    if mc.getPanel(typeOf=panel) != 'modelPanel':
        # just get the first visible model panel we find, hopefully the correct one.
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                mc.setFocus(panel)
                break

    if mc.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return False

    camShape = mc.modelEditor(panel, query=True, camera=True)
    if not camShape:
        return False

    camNodeType = mc.nodeType(camShape)
    if mc.nodeType(camShape) == 'transform':
        return camShape
    elif mc.nodeType(camShape) in ['camera', 'stereoRigCamera']:
        return mc.listRelatives(camShape, parent=True, path=True)[0]


def getFrameRate():
    """
    Return an int of the current frame rate
    """
    currentUnit = mc.currentUnit(query=True, time=True)
    if currentUnit == 'film':
        return 24
    if currentUnit == 'show':
        return 48
    if currentUnit == 'pal':
        return 25
    if currentUnit == 'ntsc':
        return 30
    if currentUnit == 'palf':
        return 50
    if currentUnit == 'ntscf':
        return 60
    if 'fps' in currentUnit:
        return int(currentUnit.replace('fps', ''))

    return 1


def getFrameRateInSeconds():
    return 1.0 / getFrameRate()


def getDistanceInMeters():
    unit = mc.currentUnit(query=True, linear=True)

    if unit == 'mm':
        return 1000
    elif unit == 'cm':
        return 100
    elif unit == 'km':
        return 0.001
    elif unit == 'in':
        return 39.3701
    elif unit == 'ft':
        return 3.28084
    elif unit == 'yd':
        return 1.09361
    elif unit == 'mi':
        return 0.000621371

    return 1


def getHoldTangentType():
    """
    Returns the best in and out tangent type for creating a hold with the current tangent settings.
    """
    try:
        tangentType = mc.keyTangent(query=True, g=True, ott=True)[0]
    except:
        return 'auto', 'auto'
    if tangentType == 'linear':
        return 'linear', 'linear'
    if tangentType == 'step':
        return 'linear', 'step'
    if tangentType == 'plateau' or tangentType == 'spline' or MAYA_VERSION < 2012:
        return 'plateau', 'plateau'
    return 'auto', 'auto'


def getIcon(name):
    """
    Check if an icon name exists, and return with proper extension.
    Otherwise return standard warning icon.
    """

    ext = '.png'
    if MAYA_VERSION < 2011:
        ext = '.xpm'

    if not name.endswith('.png') and not name.endswith('.xpm'):
        name += ext

    for each in os.environ['XBMLANGPATH'].split(os.pathsep):
        # on some linux systems each path ends with %B, for some reason
        iconPath = os.path.abspath(each.replace('%B', ''))
        iconPath = os.path.join(iconPath, name)
        if os.path.exists(iconPath):
            return name

    return None


def getIconPath():
    """
    Find the icon path
    """

    appDir = os.environ['MAYA_APP_DIR']
    for each in os.environ['XBMLANGPATH'].split(os.pathsep):
        # on some linux systems each path ends with %B, for some reason
        iconPath = each.replace('%B', '')
        if iconPath.startswith(appDir):
            iconPath = os.path.abspath(iconPath)
            if os.path.exists(iconPath):
                return iconPath


def getModelPanel():
    """
    Return the active or first visible model panel.
    """

    panel = mc.getPanel(withFocus=True)

    if mc.getPanel(typeOf=panel) != 'modelPanel':
        # just get the first visible model panel we find, hopefully the correct one.
        panels = getModelPanels()
        if panels:
            panel = panels[0]
            mc.setFocus(panel)

    if mc.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return None
    return panel


def getModelPanels():
    """
    Return all the model panels visible so you can operate on them.
    """
    panels = []
    for p in mc.getPanel(visiblePanels=True):
        if mc.getPanel(typeOf=p) == 'modelPanel':
            panels.append(p)
    return panels


def get_name_space(node):
    """
    Returns the namespace of a node with simple string parsing.
    """

    if not ':' in node:
        return ''
    return node.rsplit('|', 1)[-1].rsplit(':', 1)[0] + ':'


def getNucleusHistory(node):
    history = mc.listHistory(node, levels=0)
    if history:
        dynamics = mc.ls(history, type='hairSystem')
        if dynamics:
            nucleus = mc.listConnections(dynamics[0] + '.startFrame', source=True, destination=False, type='nucleus')
            if nucleus:
                return nucleus[0]
    return None


def get_roots(nodes):
    objs = mc.ls(nodes, long=True)
    tops = []
    namespaces = []
    parent = None
    for obj in objs:
        namespace = get_name_space(obj)
        if namespace in namespaces:
            # we've already done this one
            continue
        parent = mc.listRelatives(obj, parent=True, pa=True)
        top = obj
        if not namespace:
            while parent:
                top = parent[0]
                parent = mc.listRelatives(top, parent=True, pa=True)
            tops.append(top)
        else:
            namespaces.append(namespace)
            while parent and parent[0].rsplit('|', 1)[-1].startswith(namespace):
                top = parent[0]
                parent = mc.listRelatives(top, parent=True, pa=True)
            tops.append(top)
    return tops


def getSelectedChannels():
    """
    Return channels that are selected in the channelbox
    """

    if not mc.ls(sl=True):
        return
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    sma = mc.channelBox(gChannelBoxName, query=True, sma=True)
    ssa = mc.channelBox(gChannelBoxName, query=True, ssa=True)
    sha = mc.channelBox(gChannelBoxName, query=True, sha=True)

    channels = list()
    if sma:
        channels.extend(sma)
    if ssa:
        channels.extend(ssa)
    if sha:
        channels.extend(sha)

    return channels


def get_skin_cluster(mesh):
    """
    Return the first skinCluster affecting this mesh.
    """

    if mc.nodeType(mesh) in ('mesh', 'nurbsSurface', 'nurbsCurve'):
        shapes = [mesh]
    else:
        shapes = mc.listRelatives(mesh, shapes=True, path=True)

    for shape in shapes:
        history = mc.listHistory(shape, groupLevels=True, pruneDagObjects=True)
        if not history:
            continue
        skins = mc.ls(history, type='skinCluster')
        if skins:
            return skins[0]
    return None


def list_animation_curve(objOrAttr):
    """
    This lists connections to all types of animNodes
    """

    animNodes = list()

    tl = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTL')
    ta = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTA')
    tu = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTU')

    if tl:
        animNodes.extend(tl)
    if ta:
        animNodes.extend(ta)
    if tu:
        animNodes.extend(tu)

    return animNodes


def longest_common_substring(data):
    """
    Returns the longest string that is present in the list of strings.
    """
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0]) - i + 1):
                if j > len(substr):
                    find = data[0][i:i + j]
                    if len(data) < 1 and len(find) < 1:
                        continue
                    found = True
                    for k in range(len(data)):
                        if find not in data[k]:
                            found = False
                    if found:
                        substr = data[0][i:i + j]
    return substr

def message(msg, position='midCenterTop'):
    OpenMaya.MGlobal.displayWarning(msg)
    fadeTime = min(len(msg) * 100, 2000)
    mc.inViewMessage(amg=msg, pos=position, fade=True, fadeStayTime=fadeTime, dragKill=True)

def minimize_rotation_curves(obj):
    """
    Sets rotation animation to the value closest to zero.
    """

    rotateCurves = mc.keyframe(obj, attribute=('rotateX', 'rotateY', 'rotateZ'), query=True, name=True)

    if not rotateCurves or len(rotateCurves) < 3:
        return

    keyTimes = mc.keyframe(rotateCurves, query=True, timeChange=True)
    tempFrame = sorted(keyTimes)[0] - 1

    # set a temp frame
    mc.setKeyframe(rotateCurves, time=(tempFrame,), value=0)

    # euler filter
    mc.filterCurve(rotateCurves)

    # delete temp key
    mc.cutKey(rotateCurves, time=(tempFrame,))

class MlUi(object):
    """
    Window template for consistency
    """

    def __init__(self, name, title, width=400, height=200, info='', menu=True, module=None):

        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.info = info
        self.menu = menu

        self.module = module
        if not module or module == '__main__':
            self.module = self.name

        # look for icon
        self.icon = getIcon(name)

    def __enter__(self):
        self.buildWindow()
        return self

    def __exit__(self, *args):
        self.finish()

    def buildWindow(self):
        """
        Initialize the UI
        """

        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name)

        mc.window(self.name, title='ml :: ' + self.title, iconName=self.title, width=self.width, height=self.height,
                  menuBar=self.menu)

        if self.menu:
            self.createMenu()

        self.form = mc.formLayout()
        self.column = mc.columnLayout(adj=True)

        mc.rowLayout(numberOfColumns=2, columnWidth2=(34, self.width - 34), adjustableColumn=2,
                     columnAlign2=('right', 'left'),
                     columnAttach=[(1, 'both', 0), (2, 'both', 8)])

        # if we can find an icon, use that, otherwise do the text version
        if self.icon:
            mc.iconTextStaticLabel(style='iconOnly', image1=self.icon)
        else:
            mc.text(label=' _ _ |\n| | | |')

        """
        if not self.menu:
            mc.popupMenu(button=1)
            mc.menuItem(label='Help', command=(_showHelpCommand(TOOL_URL + self.name + '/')))
        """

        mc.text(label=self.info)
        mc.setParent('..')
        mc.separator(height=8, style='single', horizontal=True)

    def finish(self):
        """
        Finalize the UI
        """

        mc.setParent(self.form)

        frame = mc.frameLayout(labelVisible=False)
        mc.helpLine()

        mc.formLayout(self.form, edit=True,
                      attachForm=((self.column, 'top', 0), (self.column, 'left', 0),
                                  (self.column, 'right', 0), (frame, 'left', 0),
                                  (frame, 'bottom', 0), (frame, 'right', 0)),
                      attachNone=((self.column, 'bottom'), (frame, 'top')))

        mc.showWindow(self.name)
        mc.window(self.name, edit=True, width=self.width, height=self.height)

    def createMenu(self, *args):
        """
        Create the main menu for the UI
        """

        # generate shelf label by removing ml_
        shelfLabel = self.name.replace('ml_', '')
        module = self.module
        if not module:
            module = self.name

        # if icon exists, use that
        argString = ''
        if not self.icon:
            argString = ', label="' + shelfLabel + '"'

        mc.menu(label='Tools')
        mc.menuItem(label='Add to shelf', command='import animation_utilities;animation_utilities.createShelfButton("import ' + module + ';' + module + '.ui()", name="' + self.name + '", description="Open the UI for ' + self.name + '."' + argString + ')')
        if not self.icon:
            mc.menuItem(label='Get Icon', command=(_show_help_command(ICON_URL + self.name + '.png')))
        #mc.menuItem(label='Get More Tools!', command=(_showHelpCommand(WEBSITE_URL + '/tools/')))
        mc.setParent('..', menu=True)

        mc.menu(label='Help')
        mc.menuItem(label='About', command=self.about)
        #mc.menuItem(label='Documentation', command=(_showHelpCommand(TOOL_URL + self.name + '/')))
        #mc.menuItem(label='Python Command Documentation', command=(_showHelpCommand(TOOL_URL + '#\%5B\%5B' + self.name + '\%20Python\%20Documentation\%5D\%5D')))
        #mc.menuItem(label='Submit a Bug or Request', command=(_showHelpCommand(WEBSITE_URL + '/about/')))
        mc.setParent('..', menu=True)

    def about(self, *args):
        """
        This pops up a window which shows the revision number of the current script.
        """

        text = 'by Nag\n\n'
        try:
            __import__(self.module)
            module = sys.modules[self.module]
            text = text + 'Revision: ' + str(module.__revision__) + '\n'
        except ZeroDivisionError:
            pass
        try:
            text = text + 'animation_utilities Rev: ' + str(__revision__) + '\n'
        except ZeroDivisionError:
            pass
        mc.confirmDialog(title=self.name, message=text, button='Close')

    def buttonWithPopup(self, label=None, command=None, annotation='', shelfLabel='', shelfIcon='render_useBackground', readUI_toArgs={}):
        """
        Create a button and attach a popup menu to a control with options to create a shelf button or a hotkey.
        The argCommand should return a kwargs dictionary that can be used as args for the main command.
        """
        if self.icon:
            shelfIcon = self.icon
        if annotation and not annotation.endswith('.'):
            annotation += '.'
        button = mc.button(label=label, command=command, annotation=annotation + ' Or right click for more options.')
        mc.popupMenu()
        self.shelfMenuItem(command=command, annotation=annotation, shelfLabel=shelfLabel, shelfIcon=shelfIcon)
        self.hotkeyMenuItem(command=command, annotation=annotation)
        return button

    def shelfMenuItem(self, command=None, annotation='', shelfLabel='', shelfIcon='menuIconConstraints', menuLabel='Create Shelf Button'):
        """
        This creates a menuItem that can be attached to a control to create a shelf menu with the given command
        """
        pythonCommand = 'import ' + self.name + ';' + self.name + '.' + command.__name__ + '()'
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createShelfButton(\"' + pythonCommand + '\", \"' + shelfLabel + '\", \"' + self.name + '\", description=\"' + annotation + '\", image=\"' + shelfIcon + '\")',
                    enableCommandRepeat=True,
                    image=shelfIcon)

    def hotkeyMenuItem(self, command=None, annotation='', menuLabel='Create Hotkey'):
        """
        This creates a menuItem that can be attached to a control to create a hotkey with the given command
        """
        melCommand = 'import ' + self.name + ';' + self.name + '.' + command.__name__ + '()'
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createHotkey(\"' + melCommand + '\", \"' + self.name + '\", description=\"' + annotation + '\")',
                    enableCommandRepeat=True,
                    image='commandButton')

    def selectionField(self, label='', annotation='', channel=False, text=''):
        """
        Create a field with a button that adds the selection to the field.
        """
        field = mc.textFieldButtonGrp(label=label, text=text, buttonLabel='Set Selected')
        mc.textFieldButtonGrp(field, edit=True, buttonCommand=partial(self._populateSelectionField, channel, field))
        return field

    def _populateSelectionField(self, channel, field, *args):
        selectedChannels = None
        if channel:
            selectedChannels = getSelectedChannels()
            if not selectedChannels:
                raise RuntimeError('Please select an attribute in the channelBox.')
            if len(selectedChannels) > 1:
                raise RuntimeError('Please select only one attribute.')
        sel = mc.ls(sl=True)
        if not sel:
            raise RuntimeError('Please select a node.')
        if len(sel) > 1:
            raise RuntimeError('Please select only one node.')
        selection = sel[0]
        if selectedChannels:
            selection = selection + '.' + selectedChannels[0]
        mc.textFieldButtonGrp(field, edit=True, text=selection)

    def selectionList(self, channel=False, **kwargs):
        tsl = mc.textScrollList(**kwargs)
        mc.button(label='Append Selected', command=partial(self._populateSelectionList, channel, tsl))
        return tsl

    def _populateSelectionList(self, channel, control, *args):
        selectedChannels = None
        if channel:
            selectedChannels = getSelectedChannels()
            if not selectedChannels:
                raise RuntimeError('Please select an attribute in the channelBox.')
            if len(selectedChannels) > 1:
                raise RuntimeError('Please select only one attribute.')
        sel = mc.ls(sl=True)
        if not sel:
            raise RuntimeError('Please select a node.')
        if len(sel) > 1:
            raise RuntimeError('Please select only one node.')
        selection = sel[0]
        if selectedChannels:
            selection = selection + '.' + selectedChannels[0]
        mc.textScrollList(control, edit=True, append=[selection])

    class ButtonWithPopup:
        def __init__(self,
                     label=None,
                     name=None,
                     command=None,
                     annotation='',
                     shelfLabel='',
                     shelfIcon='render_useBackground',
                     readUI_toArgs={},
                     **kwargs):
            """
            The fancy part of this object is the readUI_toArgs argument.
            """
            self.uiArgDict = readUI_toArgs
            self.name = name
            self.command = command
            self.kwargs = kwargs
            self.annotation = annotation
            self.shelfLabel = shelfLabel
            self.shelfIcon = shelfIcon

            if annotation and not annotation.endswith('.'):
                annotation += '.'

            button = mc.button(label=label, command=self.runCommand, annotation=annotation + ' Or right click for more options.')
            mc.popupMenu()
            mc.menuItem(label='Create Shelf Button', command=self.createShelfButton, image=shelfIcon)
            mc.menuItem(label='Create Hotkey', command=self.createHotkey, image='commandButton')

        def readUI(self):
            """
            This reads the UI elements and turns them into arguments saved in a kwargs style member variable
            """

            if self.uiArgDict:
                # this is some fanciness to read the values of UI elements and generate or run the resulting command
                # keys represent the argument names, the values are UI elements
                for k in list(self.uiArgDict.keys()):
                    uiType = mc.objectTypeUI(self.uiArgDict[k])
                    value = None
                    if uiType == 'rowGroupLayout':
                        controls = mc.layout(self.uiArgDict[k], query=True, childArray=True)
                        if 'check1' in controls:
                            value = mc.checkBoxGrp(self.uiArgDict[k], query=True, value1=True)
                        elif 'radio1' in controls:
                            # this will be a 1 based index, we want to return formatted button name?
                            value = mc.radioButtonGrp(self.uiArgDict[k], query=True, select=True) - 1
                        elif 'slider' in controls:
                            try:
                                value = mc.floatSliderGrp(self.uiArgDict[k], query=True, value=True)

                            except Exception:
                                pass
                            try:
                                value = mc.intSliderGrp(self.uiArgDict[k], query=True, value=True)

                            except Exception:
                                pass
                        elif 'field1' in controls:
                            value = mc.floatFieldGrp(self.uiArgDict[k], query=True, value1=True)
                        elif 'OptionMenu' in controls:
                            value = mc.optionMenuGrp(self.uiArgDict[k], query=True, select=True)
                    else:
                        OpenMaya.MGlobal.displayWarning('Cannot read ' + uiType + ' UI element: ' + self.uiArgDict[k])
                        continue
                    self.kwargs[k] = value

        def runCommand(self, *args):
            """
            This compiles the kwargs and runs the command directly
            """
            self.readUI()
            self.command(**self.kwargs)

        def stringCommand(self):
            """
            This takes the command
            """
            cmd = 'import ' + self.name + '\n' + self.name + '.' + self.command.__name__ + '('
            comma = False
            for k, v in list(self.kwargs.items()):
                value = v
                if isinstance(v, str):
                    value = "'" + value + "'"
                else:
                    value = str(value)
                if comma:
                    cmd += ', '
                cmd = cmd + k + '=' + value
                comma = True
            cmd += ')'
            return cmd

        def createShelfButton(self, *args):
            """
            Builds the command and creates a shelf button out of it
            """
            self.readUI()
            pythonCommand = self.stringCommand()
            createShelfButton(pythonCommand, self.shelfLabel, self.name, description=self.annotation, image=self.shelfIcon)

        def createHotkey(self, annotation='', menuLabel='Create Hotkey'):
            """
            Builds the command and prompts to create a hotkey.
            """
            self.readUI()
            pythonCommand = self.stringCommand()
            createHotkey(pythonCommand, self.name, description=self.annotation)

class Vector:

    def __init__(self, x=0, y=0, z=0):
        """
        Initialize the vector with 3 values, or else
        """

        if self._isCompatible(x):
            x = x[0]
            y = x[1]
            z = x[2]
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'Vector({0:.2f}, {1:.2f}, {2:.2f})'.format(*self)

    # iterator methods
    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        [self.x, self.y, self.z][key] = value

    def __len__(self):
        return 3

    def _isCompatible(self, other):
        """
        Return true if the provided argument is a vector
        """
        if isinstance(other, (Vector, list, tuple)) and len(other) == 3:
            return True
        return False

    def __add__(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only add to another vector of the same dimension.')

        return Vector(*[a + b for a, b in zip(self, other)])

    def __sub__(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only subtract another vector of the same dimension.')

        return Vector(*[a - b for a, b in zip(self, other)])

    def __mul__(self, other):
        if self._isCompatible(other):
            return Vector(*[a * b for a, b in zip(self, other)])
        elif isinstance(other, (float, int)):
            return Vector(*[x * float(other) for x in self])
        else:
            raise TypeError("Can't multiply {} with {}".format(self, other))

    def __div__(self, other):
        if isinstance(other, (float, int)):
            return Vector(*[x / float(other) for x in self])
        else:
            raise TypeError("Can't divide {} by {}".format(self, other))

    def magnitude(self):
        return math.sqrt(sum([x ** 2 for x in self]))

    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
            self.z /= d
        return self

    def normalized(self):
        d = self.magnitude()
        if d:
            return self / d
        return self

    def dot(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only perform dot product with another Vector object of equal dimension.')
        return sum([a * b for a, b in zip(self, other)])

    def cross(self, other):
        if not self._isCompatible(other):
            raise TypeError('Can only perform cross product with another Vector object of equal dimension.')
        return Vector(self.y * other.z - self.z * other.y,
                      -self.x * other.z + self.z * other.x,
                      self.x * other.y - self.y * other.x)


