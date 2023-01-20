# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mm
import pymel.core as pm
from functools import partial

WINDOW_NAME = 'ReplacerWindow'

def set_path_replace():
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    path = cmds.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, okc="set", fileMode=1)[0]
    cmds.textFieldButtonGrp("RR", e=True, text=path)
    print("set_path_replace => {0}".format(path))

def set_path_save():
    path = cmds.fileDialog2(dialogStyle=2, okc="set", fileMode=3)[0]
    cmds.textFieldButtonGrp("savePath", e=True, text=path)
    print("set_path_save => {0}".format(path))

def apply_reference(args):
    rrn = cmds.textFieldButtonGrp("RR", q=True, text=True)
    savePath = cmds.textFieldButtonGrp("savePath", q=True, text=True)
    projectPath = cmds.workspace(fn=True)
    print("rrn => {0}".format(rrn))

    print("START---------------------Replaced Reference---------------")
    nodes = cmds.ls(sl=True)
    for node in nodes:
        #cur_path = mm.FileReference(node).path
        #print(cur_path)
        _node = cmds.referenceQuery(node, referenceNode=True)
        _path = cmds.referenceQuery(_node, filename=True)
        _is_loaded = cmds.referenceQuery(_node, isLoaded=True)
        _node_index = _node.find('Rig')
        if _is_loaded is False and _node_index > -1:
            print("_node => {0}".format(_node))
            print("_path => {0}".format(_path))
            cmds.file(rrn, loadReference=node)
    print("END---------------------Replaced Reference---------------")

    if cmds.checkBox("save", q=True, v=True):
        currentName = cmds.file(q=True, sceneName=True, shortName=True)
        optionSel = cmds.radioCollection("Options", q=True, sl=True)

        if optionSel == "CurrentName":
            savePath = savePath + "/" + currentName

        is_binary = False
        if optionSel == "ChangeName":
            newName = cmds.textFieldButtonGrp("sceneName", q=True, text=True)
            if "." in newName:
                savePath = savePath + "/" + newName

                if newName == "mb":
                    is_binary = True
            else:
                cmds.error(u"拡張子をつけてください")
        """
        if optionSel == "ChangeReplaceName":
            replace_oldName = cmds.textField("old", q=True, text=True)
            replace_newName = cmds.textField("new", q=True, text=True)
            newName = currentName.replace(replace_oldName, replace_newName)
            if newName == currentName:
                cmds.error(u"置き換える文字列は見つかりませんでした")
            savePath = savePath + "/" + newName
        """

        print("savePath => {0}".format(savePath))
        print("projectPath => {0}".format(projectPath))
        cmds.file(rename=savePath)
        if is_binary:
            cmds.file(save=True, force=True, type='mayaBinary')
        else:
            cmds.file(save=True, force=True, type='mayaAscii')
    else:
        print(u"保存を省略しました")

    if cmds.checkBox("ReturnSetProject", q=True, v=True):
        # mm.eval('setProject "%r"'%projectPath)
        cmds.workspace(projectPath, openWorkspace=True)

class ReplacerWindow(object):

    def __init__(self):
        if cmds.window(WINDOW_NAME, exists=True):
            cmds.deleteUI(WINDOW_NAME)

        cmds.window(WINDOW_NAME, menuBarVisible=True, tlb=True, s=1, t="ReplacerWindow", resizeToFitChildren=1, mnb=1, mxb=0)
        cmds.columnLayout('MainColumnLayout', adjustableColumn=True, rowSpacing=5, columnAttach=["both", 5])

        cmds.textFieldButtonGrp("RR", label="replace reference Path", buttonLabel="path", buttonCommand=partial(set_path_replace), annotation=u"リプレイスのパスです。ファイル名込みです")
        cmds.textFieldButtonGrp("savePath", label="save scene path", buttonLabel="path", buttonCommand=partial(set_path_save), annotation=u"セーブパスです、ファイル名は不要です")
        cmds.textFieldButtonGrp("sceneName", label="new scene name", enableButton=False, enable=False)

        cmds.rowLayout("ChangeNameWord", nc=4, cw=[1, 150], en=False)
        cmds.text("ChangeNameWord", l="Change name word")
        cmds.textField("old", w=100)
        cmds.text(">>")
        cmds.textField("new", w=100)
        cmds.setParent("..")

        cmds.checkBox("ReturnSetProject", label="Return Set Project", v=True, annotation=u"連続で処理をしやすいよう、最後にプロジェクトセットを戻します")
        #cmds.checkBox("save", label="Apply", v=False, annotation=u"保存をする場合はチェックしてください。")

        cmds.separator(h=12)
        cmds.text("Scene Name Option")

        cmds.radioCollection("Options")
        #cmds.radioButton("CurrentName", sl=True, label=u"シーン名はそのままで保存先のみを変更")
        #cmds.radioButton("ChangeName", label=u"別名保存", onc="cmds.textFieldButtonGrp('sceneName',e=True, enable=True)", ofc="cmds.textFieldButtonGrp('sceneName',e=True, enable=False)")
        """
        cmds.radioButton("ChangeReplaceName", l=u"現在のシーン名の一部を置き換える", onc="cmds.rowLayout('ChangeNameWord', e=True, en=True)", ofc="cmds.rowLayout('ChangeNameWord', e=True, en=False)")
        """
        cmds.button(label="Run", command=partial(apply_reference))
        cmds.setParent('..')
        cmds.showWindow(WINDOW_NAME)


