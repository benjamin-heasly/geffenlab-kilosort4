# Extend the official nvidia/cuda:12.0.0-base-ubuntu20.04
# Similar to the SpikeInterface kilosort4 image (https://github.com/SpikeInterface/spikeinterface-dockerfiles/tree/main/kilosort4)
# Except the SpikeInterface image is not using Conda correctly!
FROM nvidia/cuda:12.0.0-base-ubuntu20.04

# Do we neeed libfftw3-dev ?

# Install a few system dependencies, clean up cache and temp files along the way.
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt install --no-install-recommends --yes wget ca-certificates \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

# Install conda.
RUN mkdir -p /opt/conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py311_24.5.0-0-Linux-x86_64.sh -O /opt/conda/miniconda.sh \
    && bash /opt/conda/miniconda.sh -b -p /opt/miniconda

# Create our conda environment from environment.yml.
COPY environment/environment.yml .
RUN /opt/miniconda/bin/conda env create -f environment.yml

#COPY code/run.py /opt/code/run.py
#ENTRYPOINT ["/opt/miniconda/bin/conda", "run", "--no-capture-output", "-n", "kilosort4", "python", "/opt/code/run.py"]

COPY /code/test_kilosort.py /opt/code/test_kilosort.py
ENTRYPOINT ["/opt/miniconda/bin/conda", "run", "--no-capture-output", "-n", "kilosort4", "python", "/opt/code/test_kilosort.py"]
