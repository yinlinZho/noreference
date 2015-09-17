# -*- coding: utf-8 -*-
__author__ = 'LibX'

import os
import time
import log
import subprocess

default_ffmpeg_path = "D:\\software\\ffmpeg\\bin"

def extract(video_file_path, image_basedir, log_dir=default_log_dir, ffmpeg_path=default_ffmpeg_path):
    start_time = time.time()
    
    try:
        video_file_name = os.path.basename(video_file_path)
        video_name = os.path.splitext(video_file_name)[0]
        image_dir = os.path.join(image_basedir, video_name)
        image_file_pattern = os.path.join(image_dir, video_name + '%5d.bmp')
        
        logger = log.get_logger('extract', video_name)
        
        if not os.path.exists(image_dir):
            # 不存在才创建
            logger.debug('make dir %s' % (image_dir, ))
            os.makedirs(image_dir)
        
        cmd = [os.path.join(ffmpeg_path, 'ffmpeg'), '-i', video_file_path, '-r', '60', '-f', 'image2', image_file_pattern]
        logger.debug('run ffmpeg cmd %s' % (' '.join(cmd), ))
        child = subprocess.Popen(cmd, cwd=ffmpeg_path)
        child.wait()
        
        return {
            'video_name': video_name,
            'image_dir': image_dir,
            'image_files': [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ]
        }
    finally:
        end_time = time.time()
        logger.debug('extract %s spent %ds' % (video_file_path, (end_time-start_time) ))

if __name__=="__main__":
    # logging.basicConfig(level=logging.INFO)
    video_path = "H:\\finish\\douyu_lol_01_CQ.avi"
    # video_path = 'G:\\douyu_lol_01_CQ.avi'
    image_basedir = 'G:\\'
    extract(video_path, image_basedir)
