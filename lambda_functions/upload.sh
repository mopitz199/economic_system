#!/bin/bash

absolute_path=$(pwd)

cd lambda_functions

zip -r ${1}.zip ${1}/*

aws lambda update-function-code \
    --function-name "${1}" \
    --zip-file "fileb://${absolute_path}/lambda_functions/${1}.zip" \
    --region "us-east-1"

rm ${1}.zip