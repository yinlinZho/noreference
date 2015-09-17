from mlab.releases import latest_release as matlab
print '=====1====='
image = matlab.imread('img.bmp')
print '=====2====='
qualityscore = matlab.SSEQ(image)
print '=====3====='
print qualityscore
print '=====4====='