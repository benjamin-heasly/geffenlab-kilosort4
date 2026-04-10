#!/bin/sh

set -e

docker build -f environment/Dockerfile -t geffenlab/kilosort4:local .
