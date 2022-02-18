import boto3
import json
import logging

class innodbProvider():

    client = None

    def __init__(self,aws_region):
        self.client = boto3.resource('dynamodb', region_name = aws_region)


    def put(self, table, payload):
        table = self.client.Table(table)
        table.put_item(Item=payload)
        return payload, True, None
