# geffenlab-kilosort4

Docker image with Kilosort 4 and its dependencies, including the NVIDIA/CUDA version of pytorch, plus NVIDIA/CUDA dependencies from the [nvidia/cuda:12.0.0-base-ubuntu20.04](https://hub.docker.com/layers/nvidia/cuda/12.0.0-base-ubuntu20.04/images/sha256-efe596aa8220ab63b03b5d0ea873c7bd862ff2ee2f2ee2d8a789ff3b7eeb261f) base layer.

Adds Python CLI entrypoint to help with pipeline integration, things like:
 - finding one or more probes within an input run directory
 - converting SpikeGLX `.meta` files to the `.prb` format used by Kilosort
 - associating each probe with a document of Kilosort 4 parameters
 - writing sorting outputs to a configurable directory, allowing input run director to be read-only

# Building Docker image versions

This repo is configured to automatically build and publish a new Docker image version, each time a [repo tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) is pushed to GitHub.

## Published versions

The published images are located in the GitHub Container Registry as [geffenlab-kilosort4](https://github.com/benjamin-heasly/geffenlab-kilosort4/pkgs/container/geffenlab-kilosort4).  You can find the latest published version at this page.

You can access published images using their full names.  For version `v0.0.4` the full name would be `ghcr.io/benjamin-heasly/geffenlab-kilosort4:v0.0.4`.

```
docker pull ghcr.io/benjamin-heasly/geffenlab-kilosort4:v0.0.4
```

## Releasing new versions

Here's a workflow for building and realeasing a new Docker image version.

First, make changes to the code in this repo, and `push` the changes to GitHub.

```
# Edit code
git commit -a -m "Now with lasers!"
git push
```

Next, create a new repository [tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging), which marks the most recent commit as important, giving it a unique name and description.

```
# Review existing tags and choose the next version number to use.
git pull --tags
git tag -l

# Create the tag for the next version
git tag -a v0.0.5 -m "Now with lasers!"
git push --tags
```

GitHub should automatically kick off a build and publish workflow for the new tag.
You can follow the workflow progress at the repo's [Actions](https://github.com/benjamin-heasly/geffenlab-kilosort4/actions) page.

You can see the workflow code in [build-tag.yml](./.github/workflows/build-tag.yml).
