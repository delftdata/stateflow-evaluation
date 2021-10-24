import boto3
from botocore.exceptions import ClientError
import json

dynamodb = boto3.client("dynamodb")
table = dynamodb.Table("users")
# 17 lines, 11 non-appl
def user_handler(event, context):
    username = event["username"]
    password = event["password"]
    if event["type"] == "CREATE_USER":
        user_item = {username: username, password: password}
        dynamodb.put_item(TableName="users", Item=json.dump(user_item))

        return {"message": "created a user!"}
    elif event["type"] == "LOGIN_USER":
        try:
            response = table.get_item(Key={"username": username})
        except ClientError as e:
            return {"message": "user not found"}
        else:
            user = json.loads(response["Item"])
            return {"message": user["password"] == password}

def search_handler(event, context):
    pass
