# vehicle-dispatch-platform
这个项目使用 AWS 的无服务器架构创建一个车辆调度平台，根据车辆的 VIN 码返回对应的 URL。
## 技术栈
- Python 3.9+
- AWS API Gateway
- AWS Lambda
- AWS DynamoDB
## 项目结构
```
vehicle-dispatch-platform/
├── lambda_functions/
│   ├── vehicle_handler.py
│   └── requirements.txt
├── infrastructure/
│   └── cloudformation_template.yaml
├── scripts/
│   ├── deploy.sh
│   └── create_dynamodb_table.py
└── README.md
```
## 部署说明

### 前提条件：

1. 安装 AWS CLI 并配置凭证
2. 安装 Python 3.9 或更高版本

### 部署步骤：

1. **创建 DynamoDB 表**

```bash
python scripts/create_dynamodb_table.py
```
2. **部署 Lambda 函数**
```bash
cd lambda_functions
pip install -r requirements.txt -t .
zip -r ../vehicle_handler.zip .

aws iam create-role --role-name lambda-dynamodb-role --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "lambda.amazonaws.com"},"Action": "sts:AssumeRole"}]}' --region us-west-2

aws iam attach-role-policy --role-name lambda-dynamodb-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess --region us-west-2

aws iam attach-role-policy --role-name lambda-dynamodb-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --region us-west-2


aws lambda create-function \
  --function-name vehicle-dispatch-handler \
  --runtime python3.9 \
  --handler vehicle_handler.lambda_handler \
  --zip-file fileb://../vehicle_handler.zip \
  --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/lambda-dynamodb-role
```
3. **通过 CloudFormation 部署完整架构**

```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation_template.yaml \
  --stack-name vehicle-dispatch-platform \
  --capabilities CAPABILITY_IAM
```

## API 使用示例

部署完成后，您可以通过以下方式使用 API：

1. **查询车辆 URL**
```
GET https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/vehicles?vin=WDBRF87H66F757026
```

2. **添加车辆信息**
```
POST https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/vehicles
Content-Type: application/json

{
  "vin": "WDBRF87H66F757026",
  "url": "https://example.com/cars/mercedes-123"
}
```

3. **更新车辆信息**
```
PUT https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/vehicles/WDBRF87H66F757026
Content-Type: application/json

{
  "url": "https://example.com/cars/mercedes-123-updated"
}
```

4. **删除车辆信息**
```
DELETE https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/vehicles/WDBRF87H66F757026
```

5. **获取所有车辆信息**
```
GET https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/vehicles/all
```

## 注意事项

1. 在生产环境中应添加适当的身份验证和授权机制
2. 考虑为 Lambda 函数添加日志记录和监控
3. 考虑使用 AWS SAM 或 AWS CDK 进行更简单的部署
4. 适当配置 DynamoDB 的容量和扩展策略以满足流量需求

通过使用 API Gateway、Lambda 和 DynamoDB，这个系统可以自动扩展以处理不同级别的流量，同时仅为实际使用的资源付费。
