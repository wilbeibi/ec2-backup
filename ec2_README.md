README
------------------------


The program is divided in three file UI.py, doaws.py and worker.py.

UI.py in charge of parsing arguments and set up logger.

doaws.py do all the ec2 related work, including connect to region, run instance, create volume and attach it.

worker.py as the name suggests, handle with `rsync` and `dd` operation.

According to the specification, we assume user has set the environment like this:

	EC2_BACKUP_FLAGS_AWS="--key-name key_name --security-groups ports"
	EC2_BACKUP_VERBOSE=true
	AWS_CONFIG_FILE=/path/to/ec2.conf
	EC2_BACKUP_FLAGS_SSH="-i ~/path/to/key_name.pem"

And here are some examples:

    hshen4@rainman:~/tmp/ec2-backup$ python doaws.py -m dd -v vol-1f81a669 ~/Web
     
    The authenticity of host '54.85.124.145 (54.85.124.145)' can't be established.
    RSA key fingerprint is c5:e7:cc:0c:33:74:ef:bf:9c:55:6b:22:a7:4e:d9:a9.
    Are you sure you want to continue connecting (yes/no)? yes
    vol-1f81a669

And this is another verbose version:

    hshen4@rainman:~/tmp/ec2-backup$ python doaws.py -m rsync ~/unpv13e
    parsing aws config ...
    parsing config ...
    parsing ssh config ...
    start attaching...
    Connect to region: EC2Connection:ec2.us-east-1.amazonaws.com
    wating for running, current status: pending
    wating for running, current status: pending
    Running instance i-bd693eec: key wil_kp, group ports.
    Create volume: vol-cdb89fbb
    wating for available, current status: creating
    attach volume vol-cdb89fbb
    Attached volume vol-cdb89fbb to /dev/sdz
    The authenticity of host '54.85.206.192 (54.85.206.192)' can't be established.
    RSA key fingerprint is 1b:04:f3:db:0f:30:a9:83:42:e0:9a:00:26:06:da:34.
    Are you sure you want to continue connecting (yes/no)? yes
    mke2fs 1.42.8 (20-Jun-2013)
    Filesystem label=
    OS type: Linux
    Block size=4096 (log=2)
    Fragment size=4096 (log=2)
    Stride=0 blocks, Stripe width=0 blocks
    131072 inodes, 524288 blocks
    26214 blocks (5.00%) reserved for the super user
    First data block=0
    Maximum filesystem blocks=536870912
    16 block groups
    32768 blocks per group, 32768 fragments per group
    8192 inodes per group
    Superblock backups stored on blocks: 
     	32768, 98304, 163840, 229376, 294912
     
    Allocating group tables: done                            
    Writing inode tables: done                            
    Creating journal (16384 blocks): done
    Writing superblocks and filesystem accounting information: done 
     
    vol-cdb89fbb
    instance terminated
