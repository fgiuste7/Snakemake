# SGE Installation:
## https://jon.dehdari.org/tutorials/sge_install.html

# Master Servers:
sudo apt-get install gridengine-master gridengine-qmon xfonts-100dpi xfonts-75dpi

# Client Servers:
sudo apt-get install gridengine-client

# Excecution Servers
sudo apt-get install gridengine-exec


# Check if package installed:
dpkg -s <packagename>
dpkg-query -l '<regex>'




# SGE Commands: 
List administrative hosts:
qconf -sh

List excecution nodes:
qconf -sel

Check all job status:
qstat

Check running jobs:
sudo qconf -ae SM1.maas

snakemake --jobs 10 --cluster "qsub -cwd "


