# FG:5/16/2019

#---------- Disk Setup ----------#
# https://docs.gluster.org/en/latest/Quick-Start-Guide/Quickstart/#step-2-format-and-mount-the-bricks

###----- Create disk partition -----###
fdisk /dev/sdb 
# Interactive: n->p->1->(defaults)->w 

###----- Create filesystem on partition -----###
mkfs.xfs -L ${label}  /dev/sdb1

###----- Mount filesystem -----###
mount /dev/sdb1 ${Mount_directory}


#---------- Gluster Setup ----------#
# Install Gluster?
# salt 'SM1.maas' state.sls gluster.glusterFS

###----- Gluster peer probe -----###
# From SM1:
sudo gluster peer probe SM2
sudo gluster peer probe SM3
sudo gluster peer probe SM4
sudo gluster peer probe SM5
sudo gluster peer probe SM6
sudo gluster peer probe SM7
sudo gluster peer probe SM8

# From SM2:
sudo gluster peer probe SM1
# Thats it

# Confirm:
sudo gluster peer status


###----- Create GlusterFS Volume -----###
# Gluster Volume Zero:
sudo salt 'SM*' cmd.run 'mkdir -p /data/brick1/gv0'

# From any server: Replica must be a factor of total volumes, in this case 8. Therefore replica 3 arbiter 1 not allowed (same with replica 4 arbiter 1 because arbiter is meaningless in this case)
# https://docs.gluster.org/en/latest/Administrator%20Guide/Setting%20Up%20Volumes/#creating-replicated-volumes
# https://docs.gluster.org/en/v3/Administrator%20Guide/arbiter-volumes-and-quorum/
sudo gluster volume create gv0 replica 4 SM1:/data/brick1/gv0 SM2:/data/brick1/gv0 SM3:/data/brick1/gv0 SM4:/data/brick1/gv0 SM5:/data/brick1/gv0 SM6:/data/brick1/gv0 SM7:/data/brick1/gv0 SM8:/data/brick1/gv0
sudo gluster volume start gv0

# Confirm:
# 8 Tb total with 4 replicas = 2TB total
sudo gluster volume info


###----- Mount GlusterFS Volume -----###
# Mount from any Node (Ex: Head Node)
sudo mkdir /mnt/gv0
mount -t glusterfs SM1:/gv0 /mnt/gv0

# Testing:
# Copy arbitrary file to Gluster Volume 100 times:
for i in `seq -w 1 100`; do cp ${sometestfile} /mnt/gv0/copy-test-$i; done

# Number of copies in Gluster Volume: (Expect: 100)
ls -lA /mnt/gv0/copy* | wc -l

# Number of copies in each Node: (Expect 50)
sudo salt 'SM*' cmd.run '\ls -lA /data/brick1/gv0/copy* | wc -l'


###----- Mount GlusterFS Volume on all Nodes -----###
sudo salt 'SM*' cmd.run 'mkdir /mnt/gv0'
sudo salt 'SM*' cmd.run 'mount -t glusterfs $(hostname):/gv0 /mnt/gv0'


# Unmount
sudo umount /mnt/gv0
sudo salt 'SM*' cmd.run 'umount /mnt/gv0'
