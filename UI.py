#!/usr/bin/python
# -*- coding: utf-8 -*-
# volume-id validation by regex?
# 没有 -v，新建一个2x 的目录
# 没有 -m，default dd
#
#

"""
Interaction part
"""
__auther__ = "Hongyi Shen"

import sys
import argparse
import re

def usage():
    """
    Print Usage message
    """
    print '''
    usage: %s [-h] [-m method] [-v volumn-id]

    -h            Print a usage statement and exit.
    -m method     Use given method to perform backup(dd or rsync); default is dd.
    -v volume     Use the given volume instead of creating a new one.
    ''' % sys.argv[0]
    
    
parser = argparse.ArgumentParser(description='This is a ec2-backup program', add_help=False) # use customized help
parser.add_argument("-h", dest="usage", action='store_true')
parser.add_argument("-m", dest="method", nargs=1, choices=['dd', 'rsync'], help="specify to use dd or rsync")
parser.add_argument("-v", dest="volume_id", nargs=1, help="specify a volume id to attach")
parser.add_argument("dir") # directory to operate
args = parser.parse_args()



if args.method:
    print "Use method %s" % args.method
if args.volume_id:
    vol_pat = re.compile(r'vol-[0-9a-f]{8}')
    if not vol_pat.match(args.volume_id):
        print 'Incorrect volume id format'
        sys.exit(1)
    
    print "Use volume id: %s" % args.volume_id 
if args.usage:
    usage()
    sys.exit(1)




