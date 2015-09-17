# -*- coding: utf-8 -*-
__author__ = 'LibX'

import re
import Queue
import threading
import time
import subprocess
import os
import log
import logging
import csv

default_brisquequality_path = "D:\\brisquequality\\bin"

def brisquequality(image_file_path, brisquequality_path=default_brisquequality_path):
    cmd = [os.path.join(brisquequality_path, 'brisquequality'), '-im', image_file_path]
    # logger.debug('run brisquequality cmd %s' % (' '.join(cmd), ))
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=brisquequality_path)
    child.wait()
    child_out = child.stdout.read()
    child.stdout.close()
    score = child_out[31:]
    score = score.replace('\n', '').replace('\r', '')
    return score


class WorkerThread(threading.Thread):
    def __init__(self, queue, result, brisquequality_path=default_brisquequality_path, logger=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result
        self.logger = logger
        self.brisquequality_path = brisquequality_path
    
    def debug(self, *args, **kwargs):
        if self.logger is not None:
            self.logger.debug(*args, **kwargs)
    
    def run(self):
        done = False
        while not done:
            try:
                image_file_path = self.queue.get(True, 1)
                
                self.debug('brisquequality on %s' % (os.path.basename(image_file_path), ))
                score = brisquequality(image_file_path, brisquequality_path=self.brisquequality_path)
                self.debug('brisquequality score %s is %s' % (os.path.basename(image_file_path), score, ))
                self.result.append([image_file_path, score])
                
                self.queue.task_done()
            except Queue.Empty:
                self.debug('queue is empty')
                done = True
            finally:
                pass
        self.debug('worker finished')

def quality(video_name, image_file_paths, csv_basedir):
    start_time = time.time()
    try:
        logger = log.get_logger('quality', video_name)
        
        csv_file_path = os.path.join(csv_basedir, '%s.csv' % (video_name, ))
        
        queue = Queue.Queue()
        map(queue.put, image_file_paths)
        
        threads = []
        result = []
        for i in range(15):
            t = WorkerThread(queue, result, logger=logger)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
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
        logger.debug('quality %s spent %ds' % (video_name, (end_time-start_time) ))

if __name__=='__main__':
    image_dir = 'G:\\douyu_lol_01_CQ'
    image_file_paths = [ os.path.join(image_dir, _) for _ in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, _)) ]
    # image_file_paths = image_file_paths[0:30]
    quality('douyu_lol_01_CQ', image_file_paths, 'G:\\')
    # brisquequality('G:\\douyu_lol_01_CQ\\douyu_lol_01_CQ00001.bmp')
    
    '''start = time.clock()
    queue = Queue.Queue()
    rootpath = "G:\\douyu_lol_02_CQ"
    dirs = os.listdir(rootpath)
    filelist = [rootpath+os.sep+dir for dir in dirs]
    findfile(queue,filelist)
    csv_path = "G:\\douyu_lol_02_CQ.csv"

    for i in range(15):
        t = WorkerThread(queue,csv_path)
        t.start()
    queue.join()
    print time.clock()-start'''

