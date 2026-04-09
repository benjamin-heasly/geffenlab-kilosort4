#!/bin/sh

set -e

docker build -f environment/Dockerfile -t geffenlab/kilosort4:local .

mkdir -p $PWD/results
mkdir -p $PWD/kilosort_test_data
docker run --rm \
  --volume $PWD/results:/results \
  --volume $PWD/kilosort_test_data:/kilosort_test_data \
  geffenlab/kilosort4:local
