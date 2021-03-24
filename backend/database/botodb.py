import boto3
from boto3.dynamodb import table
from boto3 import resource
from botocore.exceptions import ClientError
from backend.database.errors import NotFoundException
from pydantic import BaseModel
from datetime import datetime, date
from typing import List


class BotoTable:
    def __init__(self, connection: resource = None, ddb_table: table = None):
        print("THIS")
        if not connection:
            self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")

        if not ddb_table:
            current_table = self.dynamodb.Table('yast')

            try:
                exists = current_table.table_status
                print(exists)
                self.table = current_table
            except ClientError:
                self.table = self.create_table()
        else:
            self.table = ddb_table

    def create_table(self):
        print("creating table")
        ddb_table = self.dynamodb.create_table(
            TableName="yast",
            KeySchema=[
                {
                    "AttributeName": "hash_key",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "range_key",
                    "KeyType": "RANGE"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "hash_key",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "range_key",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "uuid",
                    "AttributeType": "S"
                }
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "individual_sheets",
                    "KeySchema": [
                        {
                            "AttributeName": "uuid",
                            "KeyType": "HASH"
                        },
                        {
                            "AttributeName": "hash_key",
                            "KeyType": "RANGE"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL",
                    }
                }
            ]
        )

        return ddb_table

    def put(self, model: BaseModel):
        if not hasattr(model, "hash_key"):
            raise AttributeError("Model must contain a hash key")
        if not hasattr(model, "range_key"):
            raise AttributeError("Model must contain a range key")

        return self.table.put_item(TableName=self.table.name, Item=model.dict())

    def get_repair(self, uuid, owner):
        got = self.table.query(TableName=self.table.name, IndexName="individual_sheets", KeyConditionExpression="#u = :uuid AND hash_key = :owner",
                               ExpressionAttributeValues={
                                   ":uuid": str(uuid),
                                   ":owner": str(owner),
                               },
                               ExpressionAttributeNames={
                                   "#u": "uuid"
                               })
        try:
            return got["Items"][0]
        except KeyError:
            raise NotFoundException("No items found")

    def query_repairs(self, owner, start_date: date, valid_groups: List[str] = ["nonprivileged", ],
                      end_date: datetime = None, limit=500):
        if not end_date:
            end_date = datetime.utcnow().isoformat()
        valid_groups = {f":group{group}": group for group in valid_groups}
        results = self.table.query(TableName=self.table.name,
                                   Limit=limit,
                                   KeyConditionExpression="hash_key = :hash_key AND range_key BETWEEN :start_date AND :end_date",
                                   FilterExpression=f"#g IN ({', '.join(valid_groups.keys())})",
                                   ExpressionAttributeValues={
                                       ":hash_key": owner,
                                       ":start_date": str(start_date),
                                       ":end_date": str(end_date),
                                       **valid_groups
                                   },
                                   ExpressionAttributeNames={
                                        "#g": "group"
                                   })
        return results.get('Items', [])
