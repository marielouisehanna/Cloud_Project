import json
import random
import boto3
import uuid
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name='us-east-1')

def handler(event, context):
    """
    Main Lambda handler function for Secret Santa matching
    """
    try:
        # Parse the incoming request
        body = json.loads(event['body'])
        participants = body['participants']
        send_emails_flag = body.get('send_emails', True)
        
        # Validate minimum participants
        if len(participants) < 3:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'At least 3 participants required'
                })
            }
        
        # Generate matches
        givers = participants.copy()
        receivers = participants.copy()
        random.shuffle(receivers)
        
        # Ensure no one gets themselves
        for i in range(len(givers)):
            if givers[i]['email'] == receivers[i]['email']:
                # Swap with next person
                if i == len(givers) - 1:
                    receivers[i], receivers[0] = receivers[0], receivers[i]
                else:
                    receivers[i], receivers[i+1] = receivers[i+1], receivers[i]
        
        # Create matches list
        matches = []
        for i in range(len(givers)):
            matches.append({
                'giver': givers[i],
                'receiver': receivers[i]
            })
        
        # Save to DynamoDB
        session_id = str(uuid.uuid4())
        table = dynamodb.Table('SecretSantaMatches')
        
        table.put_item(
            Item={
                'session_id': session_id,
                'matches': matches,
                'created_at': datetime.now().isoformat(),
                'expiration_time': int((datetime.now() + timedelta(days=30)).timestamp())
            }
        )
        
        # Send emails if requested
        email_results = []
        if send_emails_flag:
            email_results = send_emails(matches)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'session_id': session_id,
                'message': 'Matches generated successfully!',
                'emails_sent': len(email_results),
                'email_status': email_results
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

def send_emails(matches):
    """
    Send email notifications to participants
    """
    results = []
    
    for match in matches:
        try:
            response = ses.send_email(
                Source='CloudUSJ1@gmail.com',  
                Destination={
                    'ToAddresses': [match['giver']['email']]
                },
                Message={
                    'Subject': {
                        'Data': '🎅 Your Secret Santa Assignment!'
                    },
                    'Body': {
                        'Html': {
                            'Data': f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f0f9ff;">
                                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                                    <h1 style="color: #667eea;">🎅 Secret Santa Assignment</h1>
                                    <p style="font-size: 18px;">Hello <strong>{match['giver']['name']}</strong>!</p>
                                    <p style="font-size: 16px;">You are the Secret Santa for:</p>
                                    <div style="background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                                        <h2 style="margin: 0; font-size: 24px;">🎁 {match['receiver']['name']} 🎁</h2>
                                    </div>
                                    <p style="font-size: 14px; color: #666;">Remember to keep it a secret! Happy gifting! 🎄</p>
                                </div>
                            </body>
                            </html>
                            """
                        }
                    }
                }
            )
            results.append({
                'email': match['giver']['email'],
                'status': 'sent',
                'message_id': response['MessageId']
            })
            print(f"Email sent to {match['giver']['email']}")
            
        except Exception as e:
            results.append({
                'email': match['giver']['email'],
                'status': 'failed',
                'error': str(e)
            })
            print(f"Failed to send email to {match['giver']['email']}: {str(e)}")
    
    return results