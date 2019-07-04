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
salt '*' cmd.run 'apt-get install munge -y'
# Copy munge key to nodes via ssh:
salt '*' cmd.run 'sudo cp /home/fgiuste/Slurm/munge.key /etc/munge/munge.key'
# Delete universal copy:
sudo rm /home/fgiuste/Slurm

#_ SLURM Setup _________________________________________#
# Install SLURM on controller:
sudo apt install slurm-wlm
# Install SLURM on nodes:
salt '*' cmd.run 'apt install slurm-wlm -y'
# Obtain compute node specs (decrease memory for OS use):
sudo salt '*' cmd.run 'slurmd -C'
# Create slurm.conf:
firefox /usr/share/doc/slurmctld/slurm-wlm-configurator.easy.html
# Copy slurm.conf to home for node access:
vim ~/Slurm/slurm.conf
# Copy slurm.conf to final location (master/Controller)
sudo cp slurm.conf /etc/slurm-llnl/slurm.conf
# Copy cgroup.conf to final location (master/Controller)
sudo cp cgroup.conf /etc/slurm-llnl/cgroup.conf
# Copy slurm.conf to final location (nodes/Compute)
sudo salt '*' cmd.run 'sudo cp /home/fgiuste/Slurm/slurm.conf /etc/slurm-llnl/slurm.conf'
# Copy slurm.conf to final location (nodes/Compute)
sudo salt '*' cmd.run 'sudo cp /home/fgiuste/Slurm/cgroup.conf /etc/slurm-llnl/cgroup.conf'


# Start munge:
sudo systemctl enable munge
sudo systemctl start munge
sudo salt '*' cmd.run 'sudo systemctl enable munge'
sudo salt '*' cmd.run 'sudo systemctl start munge'
# Start Slurm Workload Manager/Controller:
sudo systemctl enable slurmctld
sudo systemctl start slurmctld
# Start Slurm Compute Daemon:
sudo salt '*' cmd.run 'sudo systemctl enable slurmd'
sudo salt '*' cmd.run 'sudo systemctl start slurmd'

# Stop daemons:
#sudo systemctl stop munge
sudo systemctl stop slurmctld
#sudo salt '*' cmd.run 'sudo systemctl stop munge'
sudo salt '*' cmd.run 'sudo systemctl stop slurmd'

# Check slurm log:
sudo tail -n30 /var/log/slurm-llnl/slurmctld.log
# Check munge log:
sudo tail -n30 /var/log/munge/munged.log

# Reset slurm.conf:
sudo scontrol reconfigure

# Get node Status:Drain explanation:
sudo sinfo -R

# Remove Node from Status:Drain:
sudo scontrol update nodename=SM4 state=resume

# Remove Node from Cluster: (needs reason)
sudo scontrol update nodename=SM1 state=down reason="Does not recognize User:fgiuste"


#_ SLURM Job Submission _________________________________________#
sbatch -p ${PartitionName} -J ${JobName} --ntasks=1 --cpus-per-task=1 --mem=500M


#_ SLURM Administration _________________________________________#
# Cancel all jobs on partition:
scancel -u ${USER} -p ${PartitionName}

# Show all jobs:
scontrol show job

# Cancel job: scancel
# https://slurm.schedmd.com/scancel.html
scancel --ctld ${Job_ID}

# Estimate time to run:
sbatch --test-only myscript.sh

# Get Job info after completion:
sacct -j ${Job_ID} --format=JobID,JobName,MaxRSS,Elapsed

# Show job resource usage:
# https://slurm.schedmd.com/squeue.html
squeue -o "%5i %2t %4M %5D %8R  %3C %20e %15j"


#_ MISC _________________________________________#
# Stop Docker Containers on Nodes:
sudo salt '*' cmd.run 'docker stop $(docker ps -q --filter ancestor=fgiuste/neuroimaging )'

# Cleanup /tmp on Nodes as current user:
sudo salt '*' cmd.run runas=`whoami` 'rm -r /tmp/*'

# Create directory with set owner:
sudo salt '*' cmd.run 'install -o fgiuste -d /tmp_rwb'

# Cleanup created tmp directory:
sudo salt '*' cmd.run 'rm -r /tmp_rwb/*'

# Delete files NOT matching regex:
find . -type d ! -name '*_done' -delete

# Get Processes using specified port:
lsof -i:${PortNumber}

# Grep first instance +/- 5 lines:
grep -A 5 -B 5 -m1 'Exiting' slurm-180*