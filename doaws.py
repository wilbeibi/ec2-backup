#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# switch == != to is , is not
# switch '' to ""

import UI
import worker
import sys
sys.path.insert(0, '/opt/boto/lib/python2.7/site-packages/boto-2.27.0-py2.7.egg')
import os
import boto.ec2
import getopt
import time
from UI import log, verbose
ins = None
user = "fedora"



dict_ins={'image-id':          'ami-3b361952', # Ubuntu as default
          'instance-type':     't1.micro',
          'key-name':          'stevens',
          'security-groups':   'default'}

dict_aws={'key_id':            "",
          'secret_key':        "",
          'region':            "us-east-1"}

def attach(volume_id=None, src_dir="/"):
    if(verbose):
        log.info("start attaching...")
    
    """
    Attach volume
    """
    global ins

 
    conn = boto.ec2.connect_to_region(dict_aws['region'],
                                      aws_access_key_id=dict_aws['key_id'],
                                      aws_secret_access_key=dict_aws['secret_key']
    )

    
    log.info("Connect to region: " + str(conn))

    reservations = conn.run_instances(
        image_id=dict_ins['image-id'],           
        key_name=dict_ins['key-name'],
        instance_type=dict_ins['instance-type'],
        security_groups=[dict_ins['security-groups']]
    )
        
    ins = reservations.instances[0]  

    status = ins.update()
    while status != 'running':
        log.info("wating for running, current status: " + str(status))
        time.sleep(10)
        status = ins.update()
        
    log.info("Running instance %s: key %s, group %s." %(str(ins.id), dict_ins['key-name'], dict_ins['security-groups']) )

        
    if volume_id is None:
        conv = 1024*1024*1024
        sz = worker.get_size(src_dir)
        sz = int((sz+conv-1)/conv)
        vol = conn.create_volume(sz*2, ins.placement) # change size
        volume_id = vol.id
        log.info("Create volume: " + str(volume_id))
        
	status = vol.update()
	while status != 'available':
	    log.info("wating for available, current status: " + str(status) )
	    time.sleep(5)
	    status = vol.update()

    # if(verbose):
    #     print 'Attach volume ' + str(volume_id)
    log.info("attach volume " + str(volume_id))
    dest = "/dev/sdz"
    print 
    if conn.attach_volume(volume_id, ins.id , dest) == False:
        log.error("Attach failed.")
        sys.exit(1)




    log.info( "Attached volume %s to %s" %(volume_id, dest) )

    
    return ins.ip_address, '/dev/xvdz', volume_id
    

def parse_config():
    """
    parse EC2_CONFIG_FILE, retrive aws_access_key_id and aws_secret_acess_key
    """
    log.info("parsing config ...")
    try:
        aws_conf = os.environ['AWS_CONFIG_FILE']
    except KeyError:
        log.info("Environment variable AWS_CONFIG_FILE not set.")
        sys.exit(1)

    aws_conf=worker.get_path(aws_conf)
    with open(aws_conf) as f:
        for line in f:
            if line.startswith('aws_access_key_id'):
                dict_aws['key_id'] =  line[line.find('=')+1:].strip()
                
            elif line.startswith('aws_secret_access_key'):
                dict_aws['secret_key'] = line[line.find('=')+1:].strip()
                
            elif line.startswith('region'):
                dict_aws['region'] =  line[line.find('=')+1:].strip()
                
            else:
                pass

                 
        
    
def parse_AWS():
    """
    parse EC2_BACKUP_FLAGS_AWS, which determines the details of instance
    """
    log.info("parsing aws config ...")
    try:
        ins_conf = os.environ['EC2_BACKUP_FLAGS_AWS']
    except KeyError:
        log.error("Environment variable EC2_BACKUP_FLAGS_AWS not set.")
        sys.exit(1)
    
    opts, args = getopt.getopt(ins_conf.split(), "i:t:k:g:", ["image-id=","instance-type=", "key-name=", "security-groups="])
        
    for o, a in opts:
        if o in ("-k", "--key-name"):
            dict_ins['key-name'] = a
            
        elif o in ("-g", "--security-groups"):
            dict_ins['security-groups'] = a
            
        elif o in ("-i", "--image-id"):
            dict_ins['image-id'] = a
            
        elif o in ("-t", "--instance-type"):
            dict_ins['instance-type'] = a
            
        else:
            assert False, "unhandled option: " + o
            



def parse_SSH():
    """
    parse ssh option,get private key
    
    """
    log.info("parsing ssh config ...")
    try:
        ssh_conf = os.environ['EC2_BACKUP_FLAGS_SSH']
    except KeyError:
        log.error("Environment variable EC2_BACKUP_FLAGS_SSH not set.")
        sys.exit(1)
    
    lt = ssh_conf.split()
    if lt[0] == "-i":
        return lt[1].strip()
    else:
        log.error("Unrecognized ssh option")
        sys.exit(1)

def connect_attach(volume_id=None, src_dir="/"):
    """
    perform ec2 connect, create volume and attach
    """

    parse_AWS()
    parse_config()
    key = parse_SSH()
    pub_ip, dest_dev, vol_id_p = attach(volume_id, src_dir)

    
    return key, pub_ip, dest_dev, vol_id_p


if __name__ == '__main__':

    new_volume=0
    volume_id, method, src_dir = UI.interact()
    if volume_id is None:
        new_volume=1

    key, pub_ip, dest_dev, vol_id_p = connect_attach(volume_id, src_dir)
    
    if new_volume:
        r=worker.mkfs_device(dest_dev, pub_ip, user, key)
        if r!=0:
            sys.exit(r)
    mnt_path=worker.mount_device(dest_dev, pub_ip, user, key)
    # print "mount path: ", mnt_path
    # print "use method: " + method
    if method == "dd":
        r=worker.do_tarNdd(src_dir, mnt_path, pub_ip, user, key)
    else:
        r=worker.do_rsync(src_dir, mnt_path, pub_ip, user, key)
    if r!=0:
        sys.exit(r)
    
    print vol_id_p
    if ins is not None:
        ins.terminate()
        log.info("instance terminated")
