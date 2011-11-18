import pydc1394 as fw
from time import sleep

if __name__ == "__main__":
    l = fw.DC1394Library()
    cams = l.enumerate_cameras()
    cam0 = fw.Camera(l, cams[0]['guid'])

    print "Connected to: %s / %s" %(cam0.vendor, cam0.model)

    print "\nFeatures\n", "="*30
    for feat in cam0.features:
        print "%s : %s" %(feat, cam0.__getattribute__(feat).val)

    cam0.start()
    sleep(0.5)
    matrix = cam0.shot()     ## Commenting out these
    print matrix.shape       ## two lines it still hangs....
    cam0.stop()
    print "Done?"
