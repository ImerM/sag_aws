#!/usr/bin/env bash

# Build and Deploy trim_galore

cd tools/trim_galore/docker

REPO_URI=$(aws ecr describe-repositories --repository-names trim_galore --output text --query "repositories[0].repositoryUri")

if [ -z "$REPO_URI" ]
then
    REPO_URI=$(aws ecr create-repository --repository-name trim_galore  --output text --query "repository.repositoryUri")
    echo "Created repo successfully."
fi

make REGISTRY=${REPO_URI}

cd ../../../
