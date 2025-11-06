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
        budget = body.get('budget', '$20-$30')
        is_organizer = body.get('is_organizer', False)
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
                'budget': budget,
                'is_organizer': is_organizer,
                'created_at': datetime.now().isoformat(),
                'expiration_time': int((datetime.now() + timedelta(days=30)).timestamp())
            }
        )
        
        # Send emails if requested
        email_results = []
        if send_emails_flag:
            email_results = send_emails(matches, budget)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'session_id': session_id,
                'message': 'Matches generated successfully!',
                'budget': budget,
                'emails_sent': len([e for e in email_results if e['status'] == 'sent']),
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

def send_emails(matches, budget):
    """
    Send email notifications to participants with website-matching design
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
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <link href="https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@400;700&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
                            </head>
                            <body style="margin: 0; padding: 0; font-family: 'Poppins', Arial, sans-serif; background: linear-gradient(180deg, #1a3a3a 0%, #0f2626 100%);">
                                <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(180deg, #1a3a3a 0%, #0f2626 100%); padding: 40px 20px;">
                                    <tr>
                                        <td align="center">
                                            <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px;">
                                                <!-- Header -->
                                                <tr>
                                                    <td align="center" style="padding-bottom: 30px;">
                                                        <div style="font-size: 80px; margin-bottom: 20px;">🎅</div>
                                                        <h1 style="color: #ffffff; font-size: 42px; font-family: 'Mountains of Christmas', cursive; margin: 0; text-shadow: 3px 3px 10px rgba(0,0,0,0.5);">Secret Santa</h1>
                                                        <p style="color: #c5e8e0; font-size: 18px; margin: 10px 0 0 0;">Your Assignment is Here!</p>
                                                    </td>
                                                </tr>
                                                
                                                <!-- Main Content Card -->
                                                <tr>
                                                    <td style="background: rgba(255,255,255,0.95); border-radius: 16px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
                                                        <p style="color: #2c3e50; font-size: 20px; margin: 0 0 25px 0;">
                                                            Hello <strong style="color: #c9302c;">{match['giver']['name']}</strong>! 🎄
                                                        </p>
                                                        
                                                        <p style="color: #2c3e50; font-size: 16px; margin: 0 0 20px 0;">
                                                            You are the Secret Santa for:
                                                        </p>
                                                        
                                                        <!-- Receiver Box -->
                                                        <div style="background: linear-gradient(135deg, #c9302c 0%, #e74c3c 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; margin: 25px 0; box-shadow: 0 6px 20px rgba(201,48,44,0.4);">
                                                            <div style="font-size: 48px; margin-bottom: 10px;">🎁</div>
                                                            <h2 style="margin: 0; font-size: 32px; font-weight: 700;">{match['receiver']['name']}</h2>
                                                        </div>
                                                        
                                                        <!-- Budget Info -->
                                                        <div style="background: #fff7ed; border: 2px solid #fed7aa; border-radius: 12px; padding: 20px; margin: 25px 0;">
                                                            <p style="color: #c9302c; font-size: 18px; font-weight: 600; margin: 0 0 8px 0;">
                                                                💰 Gift Budget Range
                                                            </p>
                                                            <p style="color: #2c3e50; font-size: 24px; font-weight: 700; margin: 0;">
                                                                {budget}
                                                            </p>
                                                        </div>
                                                        
                                                        <!-- Footer Message -->
                                                        <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0 0 0;">
                                                            <p style="color: #2c3e50; font-size: 14px; margin: 0; text-align: center;">
                                                                🤫 <strong>Remember:</strong> Keep it a secret!<br>
                                                                Happy gifting and have a wonderful holiday season! 🎄✨
                                                            </p>
                                                        </div>
                                                    </td>
                                                </tr>
                                                
                                                <!-- Email Footer -->
                                                <tr>
                                                    <td align="center" style="padding-top: 30px;">
                                                        <p style="color: #c5e8e0; font-size: 12px; margin: 0;">
                                                            Generated by Secret Santa Generator<br>
                                                            This is an automated message, please do not reply.
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
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