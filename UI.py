#!/usr/bin/python
# -*- coding: utf-8 -*-
# volume-id validation by regex?
# 没有 -v，新建一个2x 的目录

#

"""
Interaction part
"""

import sys, os
import argparse
import re
import logging

if 'EC2_BACKUP_VERBOSE' in os.environ:
    #global verbose
    verbose = True

log = logging.getLogger('EC2-backup')
if(verbose):
    log.setLevel(logging.INFO)
else:
    log.setLevel(logging.ERROR)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

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
    


def interact():
    method = "dd"
    volume_id = None
    parser = argparse.ArgumentParser(description='This is a ec2-backup program',
                                 add_help=False) # use customized help

    parser.add_argument("-h", dest="usage", action='store_true')

    parser.add_argument("-m", dest="method", nargs=1, choices=['dd', 'rsync'],
                    help="specify to use dd or rsync")

    parser.add_argument("-v", dest="volume_id", nargs=1,
                    help="specify a volume id to attach")

    parser.add_argument("dir") # directory to operate

    args = parser.parse_args()



    if args.method:
        method = ''.join(args.method)
        
    if args.volume_id:
        str_vid = ''.join(args.volume_id)
        vol_pat = re.compile(r'vol-[0-9a-f]{8}')
        
        if not vol_pat.match(str_vid):
            log.error("Incorrect volume id format")
            sys.exit(1)
    
        volume_id = args.volume_id


    if args.usage:
        usage()
        sys.exit(1)

    
    return volume_id, method, args.dir
    
 





