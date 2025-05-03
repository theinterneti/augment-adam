#!/bin/bash
set -e

echo "Verifying Docker access in the container..."

# Check if Docker CLI is installed
if command -v docker &> /dev/null; then
    echo "Docker CLI is installed"
    docker --version
else
    echo "Docker CLI is not installed"
    exit 1
fi

# Check Docker socket
echo "Checking Docker socket..."
if [ -S /var/run/docker.sock ]; then
    echo "Docker socket exists"
    ls -la /var/run/docker.sock
else
    echo "Docker socket does not exist"
    exit 1
fi

# Check Docker socket group
echo "Checking Docker socket group..."
SOCKET_GROUP=$(stat -c '%g' /var/run/docker.sock)
echo "Docker socket group ID: $SOCKET_GROUP"

# Check current user groups
echo "Checking current user groups..."
id

# Try to run Docker command
echo "Trying to run Docker command..."
if docker ps &> /dev/null; then
    echo "Docker command succeeded!"
    docker ps
else
    echo "Docker command failed"
    
    # Try to fix permissions
    echo "Attempting to fix Docker socket permissions..."
    sudo chmod 666 /var/run/docker.sock
    
    # Try again
    if docker ps &> /dev/null; then
        echo "Docker command now works after permission fix!"
        docker ps
    else
        echo "Docker command still fails after permission fix"
        
        # Check if user is in docker group
        if groups | grep -q docker; then
            echo "User is in docker group"
        else
            echo "User is not in docker group, adding..."
            sudo usermod -aG docker $(whoami)
            echo "User added to docker group. You may need to restart the container."
        fi
    fi
fi

echo "Docker access verification completed"
