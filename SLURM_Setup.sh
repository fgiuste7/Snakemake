# SLURM Setup:

#_ Master Setup _________________________________________#
# Install munge (security keys):
apt-get install munge -y
# Generate key:
dd if=/dev/random bs=1 count=1024 >/etc/munge/munge.key

# Copy key to home for node access:
sudo cp /etc/munge/munge.key ~/Slurm/

#_ Munge Key Setup _____________________________________#
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

# Copy slurm.conf to home:
vim ~/Slurm/slurm.conf

