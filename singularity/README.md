# Singularity #

Singularity is used on MAGEO to run containers with the software and libraries needed to run specific scripts, these containers can also be used on local workstations and other HPC systems.

## Building Containers ##

There are two ways to build singularly containers, either directly as a singularity container or as a docker container then convert to singularity.

Assuming you have a Docker file you can build from the steps to build this and convert to singulariy are:
```
sudo docker build -t container_name:latest .
sudo singularity build /tmp/singularity_from_docker.sif docker-daemon://condainer_name:latest
```

When building directly a recipe / definition file is used which provides a list of commands to run to set up the container. These commonly start with a docker container and then build on this.
For MAGEO we typically start with an NVIDIA CUDA container then add the libraries we need. A simple example is provided in [basic_cuda_conda_singularity.def](basic_cuda_conda_singularity.def) which installs some additional packages from the package manager, downloads and installs miniconda and then sets up an environment with packages defined from an environment.yaml file.

To build the container use:
```
sudo singularity build /tmp/basic_cuda_conda_singularity.sif basic_cuda_conda_singularity.def
```

#### Notes for PML Internal ####

Singularity containers need to be built with sudo but can be run without so you can build on your local workstation (where you have sudo) and run on a cluster (where you don't).

Singularity containers cannot be built on networked drives, such as your home directory, so will need to be built to a local directory on your machine, such as `/tmp`

