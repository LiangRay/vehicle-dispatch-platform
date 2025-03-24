import json
import os
import boto3
import logging
from decimal import Decimal
from botocore.exceptions import ClientError

# 设置日志级别
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 初始化 DynamoDB 客户端
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('VEHICLE_TABLE_NAME', 'VehicleDispatch')
table = dynamodb.Table(table_name)

# 辅助函数 - 格式化响应
def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }

# 处理 Decimal 类型的 JSON 编码器
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o) if o % 1 else int(o)
        return super(DecimalEncoder, self).default(o)

# 根据 VIN 获取 URL
def get_url(vin):
    try:
        response = table.get_item(
            Key={'vin': vin}
        )
        item = response.get('Item')
        
        if not item:
            return build_response(404, {'error': f'未找到VIN为{vin}的车辆'})
            
        return build_response(200, {'vin': item['vin'], 'url': item['url']})
    
    except ClientError as e:
        logger.error(f"DynamoDB错误: {e.response['Error']['Message']}")
        return build_response(500, {'error': '服务器内部错误'})

# 添加或更新车辆信息
def add_or_update_vehicle(vin, url):
    try:
        response = table.put_item(
            Item={
                'vin': vin,
                'url': url
            }
        )
        return build_response(200, {'message': '车辆信息已保存', 'vin': vin, 'url': url})
    
    except ClientError as e:
        logger.error(f"DynamoDB错误: {e.response['Error']['Message']}")
        return build_response(500, {'error': '服务器内部错误'})

# 删除车辆信息
def delete_vehicle(vin):
    try:
        # 先检查是否存在
        response = table.get_item(
            Key={'vin': vin}
        )
        if 'Item' not in response:
            return build_response(404, {'error': f'未找到VIN为{vin}的车辆'})
            
        # 删除记录
        table.delete_item(
            Key={'vin': vin}
        )
        return build_response(200, {'message': f'VIN为{vin}的车辆信息已删除'})
    
    except ClientError as e:
        logger.error(f"DynamoDB错误: {e.response['Error']['Message']}")
        return build_response(500, {'error': '服务器内部错误'})

# 获取所有车辆信息
def get_all_vehicles():
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        return build_response(200, {'vehicles': items})
    
    except ClientError as e:
        logger.error(f"DynamoDB错误: {e.response['Error']['Message']}")
        return build_response(500, {'error': '服务器内部错误'})

# Lambda 处理函数
def lambda_handler(event, context):
    logger.info(f"收到事件: {event}")
    
    # 提取HTTP方法和路径
    http_method = event['httpMethod']
    path = event.get('path', '')
    
    # 处理OPTIONS请求(CORS预检)
    if http_method == 'OPTIONS':
        return build_response(200, {})
    
    # 处理不同请求类型
    if http_method == 'GET':
        # 检查是否要获取所有车辆
        if path.endswith('/all'):
            return get_all_vehicles()
        
        # 根据VIN获取URL
        query_params = event.get('queryStringParameters', {}) or {}
        vin = query_params.get('vin')
        
        if not vin:
            return build_response(400, {'error': '缺少VIN参数'})
            
        return get_url(vin)
    
    elif http_method == 'POST':
        # 添加新车辆信息
        try:
            body = json.loads(event['body'])
            vin = body.get('vin')
            url = body.get('url')
            
            if not vin or not url:
                return build_response(400, {'error': '请提供有效的VIN和URL'})
                
            return add_or_update_vehicle(vin, url)
        
        except json.JSONDecodeError:
            return build_response(400, {'error': '无效的JSON请求体'})
    
    elif http_method == 'PUT':
        # 更新车辆信息
        path_params = event.get('pathParameters', {}) or {}
        vin = path_params.get('vin')
        
        try:
            body = json.loads(event['body'])
            url = body.get('url')
            
            if not vin or not url:
                return build_response(400, {'error': '请提供有效的VIN和URL'})
                
            return add_or_update_vehicle(vin, url)
        
        except json.JSONDecodeError:
            return build_response(400, {'error': '无效的JSON请求体'})
    
    elif http_method == 'DELETE':
        # 删除车辆信息
        path_params = event.get('pathParameters', {}) or {}
        vin = path_params.get('vin')
        
        if not vin:
            return build_response(400, {'error': '请提供有效的VIN'})
            
        return delete_vehicle(vin)
    
    else:
        return build_response(405, {'error': '不支持的HTTP方法'})
