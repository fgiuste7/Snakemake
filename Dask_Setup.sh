# Dask Setup:
# http://distributed.dask.org/en/latest/setup.html

#_ Establish conda environment _____________________________________#
conda create -n dask python=3
conda activate dask

# Create ~/.condarc to define proxy
conda config

vim ~/.condarc
# copy/paste (delete brakets):
#proxy_servers:
#  - http: 170.140.138.165:8000
#  - https: 170.140.138.165:8000

#proxy_servers:
#  http: 170.140.138.165:8000
#  https: 170.140.138.165:8000


#_ Dask Scheduler: save pid when sending to bg______________________#
dask-scheduler --scheduler-file ~/Dask/scheduler.json &
daskpid=$!
### Will output host ip:port to use in workers
### Ex: tcp://170.140.138.165:8786

#_ Confirm Worker access to scheduler.json ___________________________#
sudo salt 'SM*' cmd.run 'cat /home/fgiuste/Dask/scheduler.json'

#_ Confirm access to conda:
sudo salt 'SM*' cmd.run runas=fgiuste '/home/fgiuste/miniconda3/bin/conda --version'

#_ Worker Setup: Miniconda3:v4.6.14 Docker Image______________________#
# Pull Miniconda3:
sudo salt 'SM*' cmd.run 'docker pull continuumio/miniconda3:4.6.14'
# Run:
# /data = /mnt/gv0
# /code/Dask = /home/fgiuste/Dask
sudo salt 'SM*' cmd.run 'docker run --rm -v /home/fgiuste/.condarc:/home/neuro/.condarc:r -v /mnt/gv0:/data:rw -v /home/fgiuste/Dask:/code/Dask:rw fgiuste/neuroimaging conda create -y -f /code/Dask/environment.yaml'




#_ Start workers in background ______________________#
'dask-worker --scheduler-file /code/Dask/scheduler.json'



