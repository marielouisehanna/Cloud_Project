import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    """
    Lambda handler to retrieve Secret Santa matches by session_id
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
        
        # Get table name from environment variable
        table_name = os.environ.get('TABLE_NAME', 'SecretSantaMatches')
        table = dynamodb.Table(table_name)
        
        # Retrieve the matches from DynamoDB
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'session_id': session_id,
                'matches': item.get('matches', []),
                'budget': item.get('budget', ''),
                'is_organizer': item.get('is_organizer', False),
                'created_at': item.get('created_at', '')
            })
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