#!/bin/bash

# Check if container already exists
if podman ps -a --filter name=deploy-deploy-devenv --format "{{.Names}}" | grep -q "^deploy-deploy-devenv$"; then
    echo "Container 'deploy-deploy-devenv' already exists, starting it..."
    podman start -ai deploy-deploy-devenv
else
    echo "Building image 'deploy-deploy-devenv'..."
    podman build -t deploy-deploy-devenv -f Containerfile .
    
    echo "Creating new container 'deploy-deploy-devenv'..."
    podman run --name deploy-deploy-devenv --hostname deploy-deploy-devenv -it -v ./:/mnt/deploy-deploy:rw -v deploy-deploy-root:/root:rw deploy-deploy-devenv /lib/systemd/systemd
fi
