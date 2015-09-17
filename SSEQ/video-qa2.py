# -*- coding: utf-8 -*-
__author__ = 'LibX'

def sseq(image_file_rootpath):
    from mlab.releases import latest_release as matlab
    image = matlab.imread('img.bmp')
    print matlab.SSEQ(image)

if __name__=="__main__":
    sseq('')