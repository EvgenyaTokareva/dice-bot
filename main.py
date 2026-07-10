import json
import os

def handler(event, context):
    try:
        body = json.loads(event['body'])
        if body.get('type') == 'confirmation':
            # Код подтверждения вынесите в переменную Netlify позже
            confirmation_code = os.environ.get('VK_CONFIRMATION_CODE', '9912fcbe')
            return {
                'statusCode': 200,
                'body': confirmation_code
            }
        return {
            'statusCode': 200,
            'body': 'ok'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
