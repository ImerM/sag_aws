#!/usr/bin/env bash

# Get Bucket Names from Stacks

TEMPLATES_BUCKET=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-zone --query 'Stacks[].Outputs[?OutputKey==`TemplatesBucket`].OutputValue' --output text); echo ${TEMPLATES_BUCKET}
RESULTS_BUCKET=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-pipeline --query 'Stacks[].Outputs[?OutputKey==`JobResultsBucket`].OutputValue' --output text); echo ${RESULTS_BUCKET}

# Clear Buckets

aws s3 rm --recursive s3://${TEMPLATES_BUCKET}/
aws s3 rm --recursive s3://${RESULTS_BUCKET}/

# Disable Termination Protection on Stacks

aws cloudformation update-termination-protection --no-enable-termination-protection --stack-name batch-scgenomics-tools
aws cloudformation update-termination-protection --no-enable-termination-protection --stack-name batch-scgenomics-pipeline
aws cloudformation update-termination-protection --no-enable-termination-protection --stack-name batch-scgenomics-zone

# Delete Stacks

aws cloudformation delete-stack --stack-name batch-scgenomics-tools; aws cloudformation wait stack-delete-complete --stack-name batch-scgenomics-tools
aws cloudformation delete-stack --stack-name batch-scgenomics-pipeline; aws cloudformation wait stack-delete-complete --stack-name batch-scgenomics-pipeline
aws cloudformation delete-stack --stack-name batch-scgenomics-zone; aws cloudformation wait stack-delete-complete --stack-name batch-scgenomics-zone
