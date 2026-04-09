docker pull spikeinterface/kilosort4-base:latest

# figure out default user and home dir
# docker run --rm spikeinterface/kilosort4-base whoami
# root
# docker run --rm spikeinterface/kilosort4-base env | grep HOME
# /root

# CPU mode (17 min)
# Run local script inside the kilosort4 container.
docker run \
  --rm \
  --volume "$PWD":"/kilosort-test" \
  --volume "$HOME/.kilosort":"/root/.kilosort" \
  spikeinterface/kilosort4-base \
  python /kilosort-test/test_kilosort.py


# Install AMD GPU stuff
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html#rocm-install-quick

# Reboot

# Run local script inside the kilosort4 container.
docker run \
  --rm \
  --volume "$PWD":"/kilosort-test" \
  --volume "$HOME/.kilosort":"/root/.kilosort" \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --security-opt seccomp=unconfined \
  spikeinterface/kilosort4-base \
  python /kilosort-test/test_kilosort.py
