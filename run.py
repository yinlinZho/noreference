import sys
import duplication
import extract
import quality
import Queue
import os
import log
import logging
import threading
import time
import traceback

class VideoThread(threading.Thread):
    def __init__(self, number, queue):
        threading.Thread.__init__(self)
        self.number = number
        self.queue = queue
        self.logger = logging.getLogger('')
        log.log_config('video.log')
    def run(self):
        while not self.queue.empty():
            try:
                video = self.queue.get()
                #self.logger.info('video left:'+str(self.queue.qsize()))
                print 'thread-%d running on video %s' % (self.number, video)
                self.logger.info("thread :" + video)
                self.worker(video)
                self.queue.task_done()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print ''.join(lines)

    def worker(self,video):
        video_path = video.split("\\")
        video_name = video_path[len(video_path)-1][:-4]
        image_path = "G:" + os.sep + video_name + os.sep + video_name
        csv_path = "G:\\"+video_name+".csv"
        print 'thread-%d work on video %s' % (self.number, video_name)
        #extract video
        #input:video
        #output:image_path
        self.logger.info(video_name+'extract')
        extract.extract(video,image_path)

        #remove duplications
        self.logger.info(video_name+'remove')
        try:
            duplicate_list = duplication.getdelSeq(image_path[0:18])
            dirs = os.listdir(image_path[0:18])
            paths = [image_path[0:18] + os.sep + dir for dir in dirs]
            filelist = list(set(paths).difference(set(duplicate_list)))
        except(TypeError):
            dirs = os.listdir(image_path[0:18])
            paths = [image_path[0:18] + os.sep + dir for dir in dirs]
            filelist = paths

        #create threads to count mos of each image
        self.logger.info(video_name+'quality')
        image_queue = Queue.Queue()
        map(image_queue.put,filelist)
        self.logger.info('after removing:'+str(image_queue.qsize()))
        for i in range(15):
            t = quality.ThreadCounter(image_queue,csv_path)
            t.setDaemon(True)
            t.start()
        image_queue.join()



if __name__=='__main__':
    queue = Queue.Queue()
    rootpath = 'H:\\finish'
    dirs = os.listdir(rootpath)
    paths = [rootpath + os.sep + dir for dir in dirs]
    #paths = [paths[_] for _ in range(1, 4)]
    map(queue.put,paths)
    print queue.qsize()
    for i in range(3):
        f = VideoThread(i, queue)
        f.start()
    print 'video left :'+str(queue.qsize())
    queue.join()

