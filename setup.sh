#!/usr/bin/env bash

set -e

echo "Zip Tool Scripts & Create Template Bucket"

zip -r tools.zip ./tools

aws cloudformation create-stack --stack-name batch-scgenomics-zone --template-body file://template_cfn.yml --capabilities CAPABILITY_NAMED_IAM --enable-termination-protection --output text;aws cloudformation wait stack-create-complete --stack-name batch-scgenomics-zone

echo "Copy Nested Templates to S3 for Deployment"

TEMPLATES_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-zone --query 'Stacks[].Outputs[?OutputKey==`TemplatesBucket`].OutputValue' --output text)
TEMPLATES_BUCKET_ARN=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-zone --query 'Stacks[].Outputs[?OutputKey==`TemplatesBucketArn`].OutputValue' --output text)
aws s3 cp ./pipeline/nested_templates s3://${TEMPLATES_BUCKET_NAME} --recursive

echo "Copy Build Scripts to S3 for Deployment"

aws s3 cp tools.zip s3://${TEMPLATES_BUCKET_NAME}/tools.zip
aws s3 cp ./tools/common_utils/install_ssm_agent.sh s3://${TEMPLATES_BUCKET_NAME}/install_ssm_agent.sh
rm tools.zip

cd tools

echo "Deploy SSM Automation Docs for Image and Tools Deployment"

aws cloudformation create-stack --stack-name batch-scgenomics-tools --template-body file://template_cfn.yml --capabilities CAPABILITY_NAMED_IAM --enable-termination-protection --output text --parameters ParameterKey=TemplatesBucketName,ParameterValue=${TEMPLATES_BUCKET_NAME} ParameterKey=TemplatesBucketArn,ParameterValue=${TEMPLATES_BUCKET_ARN};aws cloudformation wait stack-create-complete --stack-name batch-scgenomics-tools

ACCOUNT_ID=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-tools --query 'Stacks[].Outputs[?OutputKey==`AccountId`].OutputValue' --output text)
BUILD_AMI_DOC_NAME=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-tools --query 'Stacks[].Outputs[?OutputKey==`BuildAMIDocumentName`].OutputValue' --output text)
BUILD_TOOLS_DOC_NAME=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-tools --query 'Stacks[].Outputs[?OutputKey==`BuildToolsDocumentName`].OutputValue' --output text)

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
AMI_NAME="BatchGenomics-${TIMESTAMP}"

echo "Build & Deploy Image with SSM Automation"

EXEC_ID=$(aws ssm start-automation-execution --document-name ${BUILD_AMI_DOC_NAME}  --parameters "TargetAmiName=${AMI_NAME}" --query "AutomationExecutionId" --output text)
echo "SSM ExecId: ${EXEC_ID}"

STATUS="Started"
while [ "$STATUS" != "Success" -a "$STATUS" != "Failed" -a "$STATUS" != "TimedOut" -a "$STATUS" != "Cancelled" ]
do
    STATUS=$(aws ssm describe-automation-executions --query "AutomationExecutionMetadataList[?AutomationExecutionId==\`${EXEC_ID}\`].AutomationExecutionStatus" --output text)
    STEP=$(aws ssm describe-automation-step-executions --automation-execution-id ${EXEC_ID} --query "StepExecutions[?StepStatus=='InProgress'].StepName" --output text)
    echo "${STATUS}:${STEP}"
    sleep 120
done

if [ "$STATUS" != "Success" ]
then
    echo "AMI build '${STATUS}'."
    exit -1
fi

IMAGE_ID=$(aws ec2 describe-images --owners ${ACCOUNT_ID} --filters "Name=name,Values=${AMI_NAME}" --query 'sort_by(Images, &CreationDate)[].ImageId' --output text)
echo "Built ImageId: ${IMAGE_ID}"

echo "Build & Deploy Tools with SSM Automation"

EXEC_ID=$(aws ssm start-automation-execution --document-name ${BUILD_TOOLS_DOC_NAME} --query "AutomationExecutionId" --output text)

STATUS="Started"
while [ "$STATUS" != "Success" -a "$STATUS" != "Failed" -a "$STATUS" != "TimedOut" -a "$STATUS" != "Cancelled" ]
do
    STATUS=$(aws ssm describe-automation-executions --query "AutomationExecutionMetadataList[?AutomationExecutionId==\`${EXEC_ID}\`].AutomationExecutionStatus" --output text)
    STEP=$(aws ssm describe-automation-step-executions --automation-execution-id ${EXEC_ID} --query "StepExecutions[?StepStatus=='InProgress'].StepName" --output text)
    echo "${STATUS}:${STEP}"
    sleep 120
done

if [ "$STATUS" != "Success" ]
then
    echo "Tools build '${STATUS}'."
    exit -1
fi

echo "Deploy Pipeline Stack"

cd ..
cd pipeline

aws cloudformation create-stack --stack-name batch-scgenomics-pipeline --template-body file://template_cfn.yml --capabilities CAPABILITY_NAMED_IAM --enable-termination-protection --output text --parameters ParameterKey=TemplatesBucket,ParameterValue=${TEMPLATES_BUCKET_NAME} ParameterKey=ImageId,ParameterValue=${IMAGE_ID};aws cloudformation wait stack-create-complete --stack-name batch-scgenomics-pipeline

cd ..

FULL_INPUT=$(aws cloudformation describe-stacks --stack-name batch-scgenomics-pipeline --query 'Stacks[].Outputs[?OutputKey==`FullWorkflowInput`].OutputValue' --output text)

echo "Go to the Step Functions console and run the GenomicsWorkflow-* workflow with this as input:"

echo "${FULL_INPUT}"

echo " "
