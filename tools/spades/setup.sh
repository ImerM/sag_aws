#!/usr/bin/env bash

# Build and Deploy spades

cd tools/spades/docker

REPO_URI=$(aws ecr describe-repositories --repository-names spades --output text --query "repositories[0].repositoryUri")

if [ -z "$REPO_URI" ]
then
    REPO_URI=$(aws ecr create-repository --repository-name spades  --output text --query "repository.repositoryUri")
    echo "Created repo successfully."
fi

make REGISTRY=${REPO_URI}

cd ../../../
