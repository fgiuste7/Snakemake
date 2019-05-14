# SLURM Setup:
# https://ubuntuforums.org/showthread.php?t=2404746

#_ Munge Key Setup _____________________________________#
# Install munge (security keys):
apt-get install munge -y
# Generate key:
dd if=/dev/random bs=1 count=1024 >/etc/munge/munge.key
# Copy key to home for node access:
sudo cp /etc/munge/munge.key ~/Slurm/
# Install munge on nodes:
salt 'SM*' cmd.run 'apt-get install munge -y'
# Copy munge key to nodes via ssh:
salt 'SM*' cmd.run 'sudo cp /home/fgiuste/Slurm/munge.key /etc/munge/munge.key'
# Delete universal copy:
sudo rm /home/fgiuste/Slurm/munge.key

#_ SLURM Setup _________________________________________#
# Install SLURM on nodes:
salt 'SM*' cmd.run 'apt install slurm-wlm -y'
# Create slurm.conf:
firefox /usr/share/doc/slurmctld/slurm-wlm-configurator.easy.html
# Copy slurm.conf to home for node access:
vim ~/Slurm/slurm.conf
# Copy slurm.conf to final location (master)
sudo cp slurm.conf /etc/slurm-llnl/slurm.conf
# Copy slurm.conf to final location (nodes)
sudo salt 'SM*' cmd.run 'sudo cp /home/fgiuste/Slurm/slurm.conf /etc/slurm-llnl/slurm.conf'


sudo systemctl enable slurmctld
sudo systemctl start slurmctld
sudo salt 'SM*' cmd.run 'sudo systemctl enable slurmctld && systemctl start slurmctld'
sudo salt 'SM*' cmd.run 'sudo systemctl enable slurmd && systemctl start slurmd'



# Check log:
sudo cat /var/log/slurm-llnl/slurmctld.log

# Sync system time:
# https://www.tecmint.com/synchronize-time-with-ntp-in-linux/
# NTP=0.north-america.pool.ntp.org
sudo vim /etc/systemd/timesyncd.conf
sudo timedatectl set-ntp true
timedatectl status

sudo cp /etc/systemd/timesyncd.conf /home/fgiuste/Slurm/timesyncd.conf
sudo salt 'SM*' cmd.run 'cp /home/fgiuste/Slurm/timesyncd.conf /etc/systemd/timesyncd.conf'
