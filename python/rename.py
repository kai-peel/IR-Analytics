__author__ = 'kai'
import sys
import os


def rename(path, prefix):
    print path, prefix
    try:
        for f in os.listdir(path):
            #print f
            #print os.path.join(path, f)
            #print os.path.join(path, prefix + f)
            os.rename(os.path.join(path, f), os.path.join(path, prefix + f))
    except Exception, e:
        print 'rename:%s' % e

if __name__ == '__main__':
    try:
        cmds = sys.argv[1:]
        rename(cmds[0], cmds[1])
    except Exception, x:
        print 'usage: python rename.py input_dir prefix'
        print '    input_dir - directory for files to process.\n'
        print '    prefix - prefix add to filename.\n'
