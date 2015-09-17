# -*- coding: utf-8 -*-
__author__ = 'LibX'

import os
import sys
import re
import time
import Queue
import threading
import subprocess
import hashlib
import csv
import logging
import shutil
import numpy

default_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
default_ffmpeg_path = "D:\\software\\ffmpeg\\bin"

def get_video_name(video_file_path):
    video_file_name = os.path.basename(video_file_path)
    return os.path.splitext(video_file_name)[0]

def config_logging(video_file_path, log_dir=default_log_dir):
    video_name = get_video_name(video_file_path)
    log_file_path = os.path.join(log_dir, '%s.log' % (video_name, ))
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(name)-20s %(levelname)-10s %(message)s',
                #datefmt='%a, %d %b %Y %H:%M:%S',
                filename=log_file_path,
                filemode='a')

def extract(video_file_path, image_dir, ffmpeg_path=default_ffmpeg_path):
    '''
    ��֡
    '''
    start_time = time.time()
    video_name = get_video_name(video_file_path)
    image_file_pattern = os.path.join(image_dir, video_name + '%5d.bmp')
    
    logger = logging.getLogger('extract')
    try:
        logger.info('extract %s ' % (video_name, ))
        if not os.path.exists(image_dir):
            # �����ڲŴ���
            logger.info('make dir %s' % (image_dir, ))
            os.makedirs(image_dir)
        
        cmd = [os.path.join(ffmpeg_path, 'ffmpeg'), '-i', video_file_path, '-r', '60', '-f', 'image2', image_file_pattern]
        logger.debug('run ffmpeg cmd %s' % (' '.join(cmd), ))
        child = subprocess.Popen(cmd, cwd=ffmpeg_path)
        child.wait()
        
        return [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ]
    finally:
        end_time = time.time()
        logger.info('extract %s spent %ds' % (video_name, (end_time-start_time) ))

def duplication(video_name, image_file_paths):
    logger = logging.getLogger('duplication')
    start_time = time.time()
    try:
        logger.info('duplication %s ' % (video_name, ))
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
        logger.info('duplication %s spent %ds' % (video_name, (end_time-start_time) ))

def sseq(image_file_path):
    '''
    ����
    '''
    from mlab.releases import latest_release as matlab
    logger = logging.getLogger('quality')
    image = matlab.imread(image_file_path)
    logger.debug('call matlab to run sseq on %s' % (image_file_path, ))
    qualityscore = matlab.SSEQ(image)
    return qualityscore
    
class QualityWorkerThread(threading.Thread):
    def __init__(self, queue, result, logger=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result
        self.logger = logger
    
    def debug(self, *args, **kwargs):
        if self.logger is not None:
            self.logger.debug(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        if self.logger is not None:
            self.logger.info(*args, **kwargs)
        
    def exception(self, *args, **kwargs):
        if self.logger is not None:
            self.logger.exception(*args, **kwargs)

    def run(self):
        done = False
        try:
            while not done:
                try:
                    image_file_path = self.queue.get(True, 1)
                    
                    self.info('sseq on %s' % (os.path.basename(image_file_path), ))
                    score = sseq(image_file_path)
                    self.info('sseq score %s is %s' % (os.path.basename(image_file_path), score, ))
                    tuple = [image_file_path, score]
                    self.result.append(tuple)
                    
                    self.queue.task_done()
                except Queue.Empty:
                    self.debug('queue is empty')
                    done = True
                finally:
                    pass
            self.debug('worker finished')
        except:
            self.exception('worker error')

def quality(video_name, image_file_paths, csv_basedir):
    '''
    ͼƬ����
    '''
    logger = logging.getLogger('quality')
    start_time = time.time()
    try:
        logger.info('quality %s ' % (video_name, ))
        csv_file_path = os.path.join(csv_basedir, '%s.csv' % (video_name, ))
        
        # queue = Queue.Queue()
        # map(queue.put, image_file_paths)
        
        # threads = []
        result = []
        # for i in range(5):
            # t = QualityWorkerThread(queue, result, logger=logger)
            # t.start()
            # threads.append(t)
        
        # for t in threads:
            # t.join()
        
        for image_file_path in image_file_paths:
            score = sseq(image_file_path)
            logger.info('sseq score %s is %s' % (os.path.basename(image_file_path), score, ))
            tuple = [image_file_path, score]
            result.append(tuple)
        
        logger.info('write score to %s' % (csv_file_path,))
        with open(csv_file_path, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(['frameid','image_name','score'])
            for _ in result:
                image_file_name = os.path.basename(_[0])
                image_name = os.path.splitext(image_file_name)[0]
                image_pattern =re.compile(video_name + '(\\d+)')
                match = image_pattern.match(image_file_name)
                if match:
                    row = [match.group(1) , image_file_name] + _[1:]
                    writer.writerow(row)
    finally:
        end_time = time.time()
        logger.info('quality %s spent %ds' % (video_name, (end_time-start_time) ))

def video_quality(video_file_path, image_basedir, csv_basedir):
    logger = logging.getLogger('video_quality')
    start_time = time.time()
    try:
        video_name = get_video_name(video_file_path)
        
        logger.info('video_quality %s ' % (video_name, ))
        image_dir = os.path.join(image_basedir, video_name)
        
        # ��֡
        # image_file_paths = extract(video_file_path, image_dir)
        image_file_paths = [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ] 
        print image_file_paths[0]
        
        # ȥ��
        image_file_paths = duplication(video_name, image_file_paths)
        
        # ����
        quality(video_name, image_file_paths, csv_basedir)
        
        # ����
        # shutil.rmtree(image_dir)
        
    except:
        logger.exception('video_quality error')
    finally:
        end_time = time.time()
        logger.info('video_quality %s spent %ds' % (video_name, (end_time-start_time) ))

if __name__=="__main__":
    video_file_path = "F:\\douyu_lol_02_CQ.avi"#sys.argv[1] #"H:\\finish\\huya_lol_18_CQ.avi"
    image_basedir = "F:\\"#sys.argv[2] #'G:\\'
    config_logging(video_file_path)
    video_quality(video_file_path, image_basedir, image_basedir)
    