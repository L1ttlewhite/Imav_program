# -*- coding: UTF-8 -*-

import yaml,os

current_path = os.path.abspath(os.path.dirname(__file__))
with open(current_path + '/config/' + 'camera.yaml', 'r') as f :
    camera_yaml = yaml.load(f.read())
    window_bottom = camera_yaml['window_hsv_low']
    print window_bottom