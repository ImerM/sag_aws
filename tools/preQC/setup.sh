#!/usr/bin/env bash

# Build and Deploy preQC

cd tools/preQC/docker

REPO_URI=$(aws ecr describe-repositories --repository-names preqc --output text --query "repositories[0].repositoryUri")

if [ -z "$REPO_URI" ]
then
    REPO_URI=$(aws ecr create-repository --repository-name preqc --output text --query "repository.repositoryUri")
    echo "Created repo successfully."
fi

make REGISTRY=${REPO_URI}

cd ../../../