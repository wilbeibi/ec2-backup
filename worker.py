import os, sys
from subprocess import Popen, PIPE
from time import gmtime, strftime

from UI import log


# devnull=open(os.devnull, 'w')
devnull=sys.stdout
 
def get_path(src):
    if src==None:
        return None
    if src[0]=='~':
        src=os.path.expanduser(src)
    return os.path.abspath(src)

def get_basename(path):
    return path.split('/')[-1]

def get_destname(dir):
    return '%s_backup_%s'%(dir, strftime("%d_%b_%Y_%H_%M_%S", gmtime()))

def get_size(path='/'):
    path = get_path(path)
    p=Popen(['du', '-sb', path], stdout=PIPE, stderr=PIPE)
    r=p.wait()
    if r!=0:
        print p.stderr.read()
        return -1
    return int(p.stdout.read().split('\t')[0])

def mkfs_device(dev, rid, user, key=None):

    key =get_path(key)
    args=['ssh', '-t', '%s@%s'%(user, rid),
          'sudo', 'mkfs', '-t', 'ext4', dev]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    p=Popen(args, stdout=devnull, stderr=PIPE)
    r=p.wait()
    if r!=0:
        print p.stderr.read()
    log.info("mkfs done")
    return r

##
# mount a EBS device onto file system
# i
# mnt_path - path to be mounted
# dev      - EBS device path
# o
# mnt_path - mounted path
##
def mount_device(dev, rid, user, key=None):

    key     =get_path(key)
    mnt_path='~/backup_mnt'
    args    =['ssh', '%s@%s'%(user, rid),
              'mkdir', mnt_path]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    p=Popen(args, stdout=devnull, stderr=PIPE)
    r=p.wait()
    if r!=0:
        print p.stderr.read()
        return ''

    args=['ssh', '-t', '%s@%s'%(user, rid),
          'sudo', 'mount', '-t', 'ext4', dev, mnt_path]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    p=Popen(args, stdout=devnull, stderr=PIPE)
    r=p.wait()
    if r!=0:
        print p.stderr.read()
        return ''
    log.info("mount done")
    return mnt_path

##
# rsync backup to the cloud
# i
# src    - source dir path
# dest   - destination dir path
# rid    - identifier of the instance, can only be public IP or DNS
# user   - cloud user
# key    - private key file path
# o
# result - kv pair like [status_code, message]
##
def do_rsync(src, dest, rid, user, key=None):

    src      =get_path(src)
    key      =get_path(key)
    dir_name =get_basename(src)
    dest_name=get_destname(dir_name)
    args     =['rsync', '-ar',
               '-e', 'ssh' if key==None else 'ssh -i %s'%(key),
                src, '%s@%s:~/%s'%(user, rid, dest_name)]
    
    p1=Popen(args, stdout=devnull, stderr=PIPE)
    r=p1.wait()
    if r!=0:
        print p.stderr.read()
	return r
    
    args=['ssh', '-t', '%s@%s'%(user, rid),
          'sudo', 'mv', '~/%s'%(dest_name), '%s'%(dest)]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    
    p2=Popen(args, stdout=devnull, stderr=PIPE)
    r=p2.wait()
    if r!=0:
        print p.stderr.read()

    log.info("rsync done")
    return r

##
# tarNdd backup to the cloud
# i
# src    - source dir path
# dest   - destination dir path
# rid    - identifier of the instance, can only be public IP or DNS
# user   - cloud user
# key    - private key file path
# o
# result - kv pair like [status_code, message]
##
def do_tarNdd(src, dest, rid, user, key=None):

    src      =get_path(src)
    key      =get_path(key)
    dir_name =get_basename(src)
    dest_name=get_destname(dir_name)
    tmp_path ='/tmp/%s'%(dest_name)
    option   ='cf'

    p=Popen(['tar', option, tmp_path, src],
              stdout=devnull, stderr=PIPE)
    r=p.wait()
    if r!=0:
        os.remove(tmp_path)
        print p.stderr.read()
        return r

    args=['ssh', '%s@%s'%(user, rid),
          'dd', 'of=~/%s'%(dest_name)]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    p1=Popen(['dd', 'if=%s'%tmp_path], stdout=PIPE, stderr=PIPE)
    p2=Popen(args, stdin=p1.stdout, stdout=devnull, stderr=PIPE)
    p1.stdout.close() # http://hg.python.org/cpython/rev/abab2c53f58f/

    args=['ssh', '-t', '%s@%s'%(user, rid),
          'sudo', 'mv', '~/%s'%(dest_name), '%s'%(dest)]
    if key!=None:
        args.insert(1, '%s'%(key))
        args.insert(1, '-i')

    p3=Popen(args, stdout=devnull, stderr=PIPE)
    r=p1.wait()
    if r!=0:
        os.remove(tmp_path)
        print p1.stderr.read()
        return r
    r=p2.wait()
    if r!=0:
        os.remove(tmp_path)
        print p2.stderr.read()
        return r
    r=p3.wait()
    if r!=0:
        print p3.stderr.read()
    os.remove(tmp_path)
    log.info("tar & dd done")
    return r

# if __name__ == '__main__':
#     print get_size('~/Dropbox/Courses/CS615/HW4')