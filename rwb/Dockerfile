# 5/17/2019 (FG)
# Neuroimaging Image

FROM continuumio/miniconda3:4.6.14

#----------------------------
# Install common dependencies
#----------------------------
ENV LANG="en_US.UTF-8" \
LC_ALL="C.UTF-8"

RUN apt-get update -qq && apt-get install -yq --no-install-recommends \
       apt-utils ca-certificates curl locales unzip sudo gnupg dirmngr screen bzip2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && localedef --force --inputfile=en_US --charmap=UTF-8 C.UTF-8 \
    && chmod 777 /opt && chmod a+s /opt \
    && chmod -R 777 /home && chmod a+s /home \
    && apt-get update -qq


#---------------------------
# Create Default Entrypoint:
#---------------------------
ENV RWB_ENTRYPOINT="/home/startup.sh"

RUN if [ ! -f "$RWB_ENTRYPOINT" ]; then \
    echo '#!/usr/bin/env bash' >> $RWB_ENTRYPOINT \
    && echo 'set +x' >> $RWB_ENTRYPOINT \
    && echo 'if [ -z "$*" ]; then /usr/bin/env bash; else $*; fi' >> $RWB_ENTRYPOINT; \
    fi


ENTRYPOINT ["/home/startup.sh"]
RUN sed -i '$isource /etc/fsl/fsl.sh' $RWB_ENTRYPOINT


#----------------------------------------------------------
# NeuroDebian Keys
# http://neuro.debian.net/install_pkg.html?p=ants
# Neurodebian:
# https://github.com/neurodebian/dockerfiles/blob/88af27888a5aee76924c3b6840fc47f9cd8f63cb/dockerfiles/xenial-non-free/Dockerfile
#----------------------------------------------------------
RUN set -x \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys DD95CC430502E37EF840ACEEA5D32F012649A5A9 \
    && gpg --export DD95CC430502E37EF840ACEEA5D32F012649A5A9 > /etc/apt/trusted.gpg.d/neurodebian.gpg \
    && rm -rf "$GNUPGHOME" \
    && apt-key list | grep neurodebian

RUN { \
    echo 'deb http://neuro.debian.net/debian stretch main'; \
    echo 'deb http://neuro.debian.net/debian data main'; \
    echo '#deb-src http://neuro.debian.net/debian-devel stretch main'; \
} > /etc/apt/sources.list.d/neurodebian.sources.list

RUN sed -i -e 's,main *$,main contrib non-free,g' /etc/apt/sources.list.d/neurodebian.sources.list; grep -q 'deb .* multiverse$' /etc/apt/sources.list || sed -i -e 's,universe *$,universe multiverse,g' /etc/apt/sources.list

#---------------------
# NeuroDebian Packages
#---------------------
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends convert3d \
                                                     ants \
                                                     fsl \
                                                     fsl-atlases \
                                                     tree \
                                                     vim \
                                                     emacs-nox \
                                                     nano \
                                                     ncdu \
                                                     graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


#-----------------------
# Create new user: neuro
#-----------------------
RUN useradd --no-user-group --create-home --shell /bin/bash neuro
USER neuro

ENV PROFILE='/home/neuro/.profile'
RUN echo "$isource /etc/fsl/fsl.sh" >> $PROFILE
RUN echo "alias ls='ls -lha --color=auto' " >> $PROFILE
RUN echo "alias rm='rm -i' " >> $PROFILE

#-------------------------
# Conda Install
#-------------------------
USER neuro

RUN conda install -y pytest \
                     traits \
                     pandas \
                     dask \
                     matplotlib \
                     scikit-learn \
                     scikit-image \
                     seaborn \
                     nibabel \
                     scipy \
                     graphviz \
                     python-graphviz \
                     networkx \
                     pydot \
                     h5py \
                     pytables \
                     zarr \
    && sync && conda clean -tipsy && sync \
    && pip install --no-cache-dir https://github.com/nipy/nipype/tarball/master \
                                  https://github.com/INCF/pybids/tarball/master \
                                  nilearn \
                                  datalad[full] \
                                  nipy \
                                  duecredit \
                                  dask==0.18.1 \
    && sync

RUN bash -c "rm -rf /opt/conda/pkgs/*"

#-----------------------------------------
# Set Directory Structure and Permissions:
#-----------------------------------------
USER root

RUN chmod -R 777 /etc/fsl
RUN chmod -R 777 /home/neuro
RUN mkdir /data && chmod -R 777 /data
RUN mkdir /output && chmod -R 777 /output
RUN chmod 777 /home/startup.sh

RUN mkdir -p /code/scripts \
    && mkdir -p /code/notebooks \
    && chmod -R 777 /code

RUN mkdir -p /app \
    && chmod -R 777 /app

#----------------------------------------
# Add ANTS directory to PATH and ANTSPATH
# Switch to user neuro
#----------------------------------------
USER neuro

ENV PATH=$PATH:/usr/lib/ants/
ENV ANTSPATH=/usr/lib/ants/

#--------------------------------------
# Make bash the default shell for neuro
#--------------------------------------
USER root
RUN chsh -s /bin/bash neuro

#----------------------------------
# Define ROOT password: FOR TESTING
#----------------------------------
USER root
RUN echo "root:Docker!" | chpasswd

#----------------------------
# RWB Specific:
# Add scripts to final image:
#----------------------------
USER root
RUN mkdir -p /code
RUN chmod 777 -R /code

#---------------------
# Login as user: neuro
#---------------------
USER neuro
ENV ls='ls -lh --color=auto'
WORKDIR /home/neuro

USER root
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
