# -*- coding: utf-8 -*-
__author__ = 'LibX'

import os
import hashlib
import time
import log
import logging

def duplication(image_file_paths):
    start_time = time.time()
    try:
        image_file_md5s = {}
        for image_file_path in image_file_paths:
            md5obj = hashlib.md5()
            with file(image_file_path,'rb') as f:
                md5obj.update(f.read())
            md5 = md5obj.hexdigest()
            if md5 not in image_file_md5s:
                image_file_md5s[md5] = image_file_path
        return image_file_md5s.values()
    finally:
        end_time = time.time()
        print (end_time-start_time)

if __name__=='__main__':
    image_dir = 'G:\\douyu_lol_01_CQ'
    image_file_paths = [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ]
    # image_file_paths = image_file_paths[0:30]
    image_file_paths = duplication(image_file_paths)
    print len(image_file_paths)
    # brisquequality('G:\\douyu_lol_01_CQ\\douyu_lol_01_CQ00001.bmp')
