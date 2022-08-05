# -*- coding: utf-8 -*-

import maya.cmds as mc

class AboutMenu:

    def __init__(self):
        if mc.window('AboutFacial', exists=True):
            mc.deleteUI('AboutFacial')
        windowAbout = mc.window('AboutFacial', title='About this script', resizeToFitChildren=False, h=400, sizeable=True, w=500)
        mc.frameLayout(labelVisible=0)
        mc.text(l='Speed Facial Rig:', fn='boldLabelFont')
        mc.columnLayout()
        mc.text(l='Current Version: 2.0', fn='boldLabelFont')
        mc.separator(h=10, style='none')
        mc.separator(h=10, style='none')
        mc.text(l='All Tutorial could be found at:')
        tutoVimeo = str('<!DOCTYPE html> <html> <a href="https://vimeo.com/album/3982065" target="_top"> https://vimeo.com/album/3982065</a><a href="https://vimeo.com/album/3982065" target="_top"> </html>')
        tutoYoutube = str('!')
        mc.rowLayout(nc=2)
        mc.text(l='Vimeo Link:  ', fn='boldLabelFont')
        mc.text(l=tutoVimeo, hl=True)
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.text(l='Youtube Link:', fn='boldLabelFont')
        mc.text(l=tutoYoutube, hl=True)
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.text(l='If you find a bug, or have any request on the dev, you can contact me at:')
        HelpEmail = str('<!DOCTYPE html> <html> <a href="https://ludovic.faucillon@gmail.com" target="_top"> ludovic.faucillon@gmail.com</a><a href="https://ludovic.faucillon@gmail.com" target="_top"> </html>')
        mc.text(l=HelpEmail, hl=True, fn='boldLabelFont')
        mc.setParent('..')
        mc.setParent('..')
        mc.text(l='Special Thanks:', fn='boldLabelFont')
        mc.columnLayout()
        mc.rowLayout(nc=2)
        mc.text(l='Norman Studio / Onyx Film: ', fn='boldLabelFont')
        mc.text(l='To trust into the Facial Rig and their collaboration to have make a movie with it')
        mc.setParent('..')
        mc.text(l='Community of Creative Crash Website', fn='boldLabelFont')
        mc.text(l='Nicolas Galvanni (head of rigging in Norman Studio) / Thierry Defossez (beta test) / Fabien Coulon (producer at Norman Studio)', fn='boldLabelFont')
        mc.text(l='Marion Balacey (UKDP) for her permission to include her script', fn='boldLabelFont')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(windowAbout)

def launchAboutMenu(*args):
    AboutMenu()
    pass
