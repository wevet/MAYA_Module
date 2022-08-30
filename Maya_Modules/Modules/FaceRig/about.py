# -*- coding: utf-8 -*-

import maya.cmds as mc


class AboutMenu:
    def __init__(self):
        if mc.window('AboutFacial', exists=True):
            mc.deleteUI('AboutFacial')
        windowAbout = mc.window('AboutFacial', title='About this script', resizeToFitChildren=False, h=400, sizeable=True, w=500)
        mc.frameLayout(labelVisible=0)
        mc.text(l='Custom Facial Rig:', fn='boldLabelFont')
        mc.columnLayout()
        mc.text(l='Current Version: 1.0', fn='boldLabelFont')
        mc.separator(h=10, style='none')
        mc.separator(h=10, style='none')
        mc.rowLayout(nc=2)
        mc.text(l='If you find a bug, or have any request on the dev, you can contact me at:')
        HelpEmail = str('<!DOCTYPE html> <html> example@gmail.com</html>')
        mc.text(l=HelpEmail, hl=True, fn='boldLabelFont')
        mc.setParent('..')
        mc.setParent('..')
        mc.text(l='Special Thanks:', fn='boldLabelFont')
        mc.columnLayout()
        mc.rowLayout(nc=2)
        mc.text(l='To trust into the Facial Rig and their collaboration to have make a movie with it')
        mc.setParent('..')
        mc.text(l='Community of Creative Crash Website', fn='boldLabelFont')
        mc.text(l='Develop by Naga for her permission to include her script', fn='boldLabelFont')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(windowAbout)

def launchAboutMenu(*args):
    AboutMenu()
