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
sudo rm /home/fgiuste/Slurm

#_ SLURM Setup _________________________________________#
# Install SLURM on nodes:
salt 'SM*' cmd.run 'apt install slurm-wlm -y'
# Obtain compute node specs (decrease memory for OS use):
sudo salt 'SM*' cmd.run 'slurmd -C'
# Create slurm.conf:
firefox /usr/share/doc/slurmctld/slurm-wlm-configurator.easy.html
# Copy slurm.conf to home for node access:
vim ~/Slurm/slurm.conf
# Copy slurm.conf to final location (master)
sudo cp slurm.conf /etc/slurm-llnl/slurm.conf
# Copy slurm.conf to final location (nodes)
sudo salt 'SM*' cmd.run 'sudo cp /home/fgiuste/Slurm/slurm.conf /etc/slurm-llnl/slurm.conf'


# Start munge:
sudo systemctl enable munge
sudo systemctl start munge
sudo salt 'SM*' cmd.run 'sudo systemctl enable munge'
sudo salt 'SM*' cmd.run 'sudo systemctl start munge'
# Start Slurm Workload Manager:
sudo systemctl enable slurmctld
sudo systemctl start slurmctld
# Start Slurm Compute Daemon:
sudo salt 'SM*' cmd.run 'sudo systemctl enable slurmd'
sudo salt 'SM*' cmd.run 'sudo systemctl start slurmd'

# Stop daemons:
#sudo systemctl stop munge
sudo systemctl stop slurmctld
#sudo salt 'SM*' cmd.run 'sudo systemctl stop munge'
sudo salt 'SM*' cmd.run 'sudo systemctl stop slurmd'

# Show all jobs:
scontrol show job

# Check slurm log:
sudo tail -n30 /var/log/slurm-llnl/slurmctld.log
# Check munge log:
sudo tail -n30 /var/log/munge/munged.log

# Resert slurm.conf:
sudo scontrol reconfigure

# Get node Status:Drain explanation:
sudo sinfo -R

# Remove Node from Status:Drain:
sudo scontrol update nodename=SM4 state=resume

# Remove Node from Cluster: (needs reason)
sudo scontrol update nodename=SM1 state=down reason="Does not recognize User:fgiuste"

# Sync system time:
# https://www.tecmint.com/synchronize-time-with-ntp-in-linux/
# NTP=0.north-america.pool.ntp.org
sudo vim /etc/systemd/timesyncd.conf
sudo timedatectl set-ntp true
timedatectl status

sudo cp /etc/systemd/timesyncd.conf /home/fgiuste/Slurm/timesyncd.conf
sudo salt 'SM*' cmd.run 'cp /home/fgiuste/Slurm/timesyncd.conf /etc/systemd/timesyncd.conf'
