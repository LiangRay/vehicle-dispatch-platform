#创建DynamoDB表
python scripts/create_dynamodb_table.py

#部署 Lambda 函数
cd lambda_functions
pip install -r requirements.txt -t .
zip -r ../vehicle_handler.zip .
aws lambda create-function \
  --function-name vehicle-dispatch-handler \
  --runtime python3.9 \
  --handler vehicle_handler.lambda_handler \
  --zip-file fileb://../vehicle_handler.zip \
  --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/lambda-dynamodb-role

#通过 CloudFormation 部署完整架构
aws cloudformation deploy \
  --template-file infrastructure/cloudformation_template.yaml \
  --stack-name vehicle-dispatch-platform \
  --capabilities CAPABILITY_IAM

