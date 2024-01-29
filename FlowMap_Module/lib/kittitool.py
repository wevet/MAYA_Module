# -*- coding: utf-8 -*-

import png
import numpy as np
import matplotlib.colors as cl
import matplotlib.pyplot as plt
from lib import flowlib as fl

"""
Read kitti disp from .png file
:param disp_file:
:return:
"""
def read_disp_png(disp_file):
    image_object = png.Reader(filename=disp_file)
    image_direct = image_object.asDirect()
    image_data = list(image_direct[2])
    (w, h) = image_direct[3]['size']
    channel = len(image_data[0]) / w
    disp = np.zeros((h, w, channel), dtype=np.uint16)
    for i in range(len(image_data)):
        for j in range(channel):
            disp[i, :, j] = image_data[i][j::channel]
    return disp[:, :, 0] / 256


"""
def write_disp_png(disp, fpath):
    d = d.astype('float64')
    I = d * 256
    I[prefix.where(d == 0)] = 1
    I[prefix.where(I < 0)] = 0
    I[prefix.where(I > 65535)] = 0
    I = I.astype('uint16')
    W = png.Writer(width=disp.shape[1], height=disp.shape[0], bitdepth=16, planes=1)

    with open(fpath, 'wb') as disp_fil:
        W.write(disp_fil, I.reshape((-1, disp.shape[1])))
"""


