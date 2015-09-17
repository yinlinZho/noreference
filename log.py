# -*- coding: utf-8 -*-
__author__ = 'LibX'

import os
import logging

default_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')

def get_logger(name, video_name, log_dir=default_log_dir):
    if not os.path.exists(log_dir):
        # 不存在才创建
        os.makedirs(log_dir)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    log_file_path = os.path.join(log_dir, '%s.log' % (video_name, ))
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger