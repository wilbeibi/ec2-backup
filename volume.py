#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Create an instance
'''



import sys
# sys.path.insert(0, '/opt/boto/lib/python2.7/site-packages/boto-2.27.0-py2.7.egg')
import os
import boto.ec2
import getopt

key_id = 'AKIAIPID4EFXEK4RHUXA'
secret_key = '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'
region = 'us-east-1'
verbose = False


dict_ins={'image-id':          'ami-3b361952', # Fedora as default
          'instance-type':     't1.micro',
          'key-name':          'stevens',
          'security-groups':   'default'}

dict_aws={'key_id':            '',
          'secret_key':        '',
          'region':            'us-east-1'}

def attach():
    """
    Attach volume
    """
    conn = boto.ec2.connect_to_region(region,
                                      aws_access_key_id=key_id,
                                      aws_secret_access_key=secret_key)

    if(verbose):
        print 'Connect to region: ' + region

    reservations = conn.run_instances(
        image_id=dict_ins['image-id'],           
        key_name=dict_ins['key-name'],
        instance_type=dict_ins['instance-type'],
        security_groups=dict_ins['security-groups'])
        
    ins = reservations[0].instances[0]

    if(verbose):
        print 'Running instance ' + str(ins.id)
    
    vol = conn.create_volume(2, ins.placement)

    if(verbose):
        print 'Create volume ' + str(vol.id)

    dest = "/dev/sdx"
    conn.attach_volume(vol.id, ins.id , dest) 

    if(verbose):
        print 'Attached volume %s to %s' %(vol.id, dest)

def parse_config():
    """
    parse EC2_CONFIG_FILE, retrive aws_access_key_id and aws_secret_acess_key
    """
    try:
        aws_conf = os.environ['AWS_CONFIG_FILE']
    except KeyError:
        print "Environment variable AWS_CONFIG_FILE not set yet."
        sys.exit(1)
    
    with open(aws_conf) as f:
        for line in f:
            if line.startswith('aws_access_key_id'):
                dict_aws['key_id'] =  line[line.find('=')+1:]
            elif line.startswith('aws_secret_access_key'):
                dict_aws['secret_key'] = line[line.find('=')+1:]
            elif line.startswith('region'):
                dict_aws['region'] =  line[line.find('=')+1:]
            else:
                pass

                 
        
    
def parse_AWS():
    """
    parse EC2_BACKUP_FLAGS_AWS, which determines the details of instance
    """
    try:
        ins_conf = os.environ['EC2_BACKUP_FLAGS_AWS']
    except KeyError:
        print "Environment variable EC2_BACKUP_FLAGS_AWS not set yet."
        sys.exit(1)
    
#    ins_conf = " --image-id ami-c3b8d6aa --instance-type t1.micro --key-name MyKeyPair --security-groups MySecurityGroup " 
    
    opts, args = getopt.getopt(ins_conf.split(), "i:t:k:g:", ["image-id=","instance-type=", "key-name=", "security-groups="])
        
    for o, a in opts:
        if o in ("-k", "--key-name"):
            #print "--key-name",a
            dict_ins['key-name'] = a
        elif o in ("-g", "--security-groups"):
            #print "security-groups",a
            dict_ins['security-groups'] = a
        elif o in ("-i", "--image-id"):
            #print "image-id",a
            dict_ins['image-id'] = a
        elif o in ("-t", "--instance-type"):
            #print "instance-type",a
            dict_ins['instance-type'] = a
        else:
            assert False, "unhanded option: " + o

    if 'EC2_BACKUP_VERBOSE' in os.environ:
        global verbose = True

  
    
if __name__ == '__main__':
    parse_AWS()
    parse_config()
    attach()









