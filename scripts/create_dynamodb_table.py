import boto3

def create_vehicle_table(table_name='VehicleDispatch'):
    """创建车辆调度DynamoDB表"""
    dynamodb = boto3.resource('dynamodb')
    
    # 创建表
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'vin',
                'KeyType': 'HASH'  # 分区键
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'vin',
                'AttributeType': 'S'  # 字符串类型
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    # 等待表创建完成
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"表 {table_name} 已创建成功，状态: {table.table_status}")

if __name__ == "__main__":
    create_vehicle_table()
