# -*- coding: utf-8 -*-

from lib import flowlib as fl
from lib import kittitool as tool
from lib import normal_map_generator as normal_map

if __name__ == '__main__':
    diffuse = 'src/sample.png'
    normal = 'src/sample_n.png'
    flow_map = 'src/sample_flow.png'
    flow_file_middle = 'src/flow_gt.flo'

    read_texture = fl.read_flow(diffuse)
    fl.visualize_flow(read_texture, mode='Y')

    #flow_Middlebury = fl.read_flow(flow_file_middle)
    #fl.visualize_flow(flow_Middlebury)

    """
    @TODO
    Lossy conversion from float64 to uint8. Range [0, 1]. 
    Convert image to uint8 prior to saving to suppress this warning.
    ./normal_map_generator.py input_file output_file --smooth SMOOTH_VALUE -- intensity INTENSITY_VALUE
    """
    #normal_map.create(smooth=0, intensity=1, input_file=diffuse, output_file=normal)

