import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    """
    Lambda handler to retrieve Secret Santa matches by session ID
    Used for organizer CSV download
    """
    try:
        # Get session_id from query parameters
        session_id = event.get('queryStringParameters', {}).get('session_id')
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'session_id is required'
                })
            }
        
        # Get matches from DynamoDB
        table = dynamodb.Table('SecretSantaMatches')
        
        response = table.get_item(
            Key={
                'session_id': session_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Session not found'
                })
            }
        
        item = response['Item']
        
        # Check if organizer access was requested
        if not item.get('is_organizer', False):
            return {
                'statusCode': 403,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Access denied. This session was not created with organizer access.'
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'session_id': session_id,
                'matches': item['matches'],
                'budget': item.get('budget', 'Not specified'),
                'created_at': item['created_at']
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }
