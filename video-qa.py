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
import log
default_roi_path = "C:\\ROI"
default_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
default_ffmpeg_path = "C:\\ffmpeg\\bin"
default_brisquequality_path = "C:\\algorithm\\brisque"

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
    解帧
    '''
    start_time = time.time()
    video_name = get_video_name(video_file_path)
    image_file_pattern = os.path.join(image_dir, video_name + '%5d.bmp')
    
    logger = logging.getLogger('extract')
    try:
        logger.info('extract %s ' % (video_name, ))
        if not os.path.exists(image_dir):
            # 不存在才创建
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
            else:
                os.remove(image_file_path)
        return image_file_md5s.values()
    finally:
        end_time = time.time()
        logger.info('duplication %s spent %ds' % (video_name, (end_time-start_time) ))
        
def removeMargin(image_file_path,feature,roi_path = default_roi_path):
    logger = logging.getLogger('roi')
    cmd = [os.path.join(roi_path, "ROI2"), " -s2 ",image_file_path,' '+image_file_path,' '+feature[0],' '+feature[1],' '+feature[2],' '+feature[3]]
    #cmd = [os.path.join(roi_path, "ROI2"), " -auto ",image_file_path,' '+os.path.join("D:\\newyy_05",os.path.basename(image_file_path))]
    cmd = ''.join(cmd)
    logger.debug('run roi cmd %s' % (' '.join(cmd), ))
    print cmd
    child = subprocess.Popen(cmd,shell = True)
    child.wait()
   
    
def brisquequality(image_file_path, brisquequality_path=default_brisquequality_path):
    '''
    评分
    '''
    logger = logging.getLogger('quality')
    cmd = [os.path.join(brisquequality_path, 'brisquequality'), '-im', image_file_path]
    logger.debug('run brisquequality cmd %s' % (' '.join(cmd), ))
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=brisquequality_path)
    child.wait()
    child_out = child.stdout.read()
    child.stdout.close()
    score = child_out[31:]
    score = score.replace('\n', '').replace('\r', '')
    return score

class QualityWorkerThread(threading.Thread):
    def __init__(self, queue, result,feature ,brisquequality_path=default_brisquequality_path, roi_path = default_roi_path,logger=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result
        self.logger = logger
        self.brisquequality_path = brisquequality_path
        self.roi_path = roi_path
        self.feature = feature
        
    
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
                    print image_file_path
                    self.info('roi on %s' % (os.path.basename(image_file_path), ))
                    
                    #removeMargin(image_file_path, self.feature,roi_path=self.roi_path)
           
                    self.info('brisquequality on %s' % (os.path.basename(image_file_path), ))
                    score = brisquequality(image_file_path, brisquequality_path=self.brisquequality_path)
           
                    self.info('brisquequality score %s is %s' % (os.path.basename(image_file_path), score, ))
                    self.result.append([image_file_path, score])
                    
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
    图片评分
    '''
    logger = logging.getLogger('quality')
    start_time = time.time()
    try:
        logger.info('quality %s ' % (video_name, ))
        csv_file_path = os.path.join(csv_basedir, '%s.csv' % (video_name, ))
        
        queue = Queue.Queue()
        map(queue.put, image_file_paths)
        cmd = [os.path.join(default_roi_path, "ROI2"), " -s1 ",image_file_paths[0]]
        cmd = ''.join(cmd)
        print cmd
        output = os.popen(cmd)
        features = output.readlines()[3:7]
        feature = []
        for _ in features:
           feature.append(_[:-1])
        print feature
        threads = []
        result = []
        for i in range(5):
            t = QualityWorkerThread(queue, result,feature, logger=logger)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        logger.info('write score to %s' % (csv_file_path,))
        with open(csv_file_path, 'wb') as f:
            writer = csv.writer(f)
            for _ in result:
                image_file_name = os.path.basename(_[0])
                image_name = os.path.splitext(image_file_name)[0]
                image_pattern =re.compile(video_name + '(\\d+)')
                match = image_pattern.match(image_file_name)
                
                if match:
                    writer.writerow([match.group(1) , image_file_name, _[1]])
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
        
        # 解帧
        #image_file_paths = extract(video_file_path, image_dir)
        # [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ] 

        path_list = os.listdir(image_dir)
        image_file_paths = []
        for _ in path_list:
            image_file_paths.append(os.path.join(image_dir,_))
       
        # 去重
        #image_file_paths = duplication(video_name, image_file_paths)
        
        #duplication(video_name, image_file_paths)
        #print image_dir
        #removeMargin(image_dir)
        # 评分
        quality(video_name, image_file_paths, csv_basedir)
        
        # 清理
        #shutil.rmtree(image_dir)
        
    except:
        logger.exception('video_quality error')
    finally:
        end_time = time.time()
        logger.info('video_quality %s spent %ds' % (video_name, (end_time-start_time) ))

if __name__=="__main__":
    video_file_path = sys.argv[1] #"H:\\finish\\huya_lol_18_CQ.avi"
    image_basedir =  sys.argv[2] #'G:\\'
    config_logging(video_file_path)
    video_quality(video_file_path, image_basedir, image_basedir)
    
    
    
