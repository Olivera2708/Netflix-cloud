import jwt
import json
import urllib.request
import os
import jwt.algorithms

def admin_authorizer(event, context):
    try:
        token = event['headers']['authorization'].split()[1]
    except:
        token = event['headers']['Authorization'].split()[1]

    user_pool_id = os.environ['USER_POOL_ID']
    
    keys_url = f"https://cognito-idp.eu-central-1.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode('utf-8'))['keys']
    
    headers = jwt.get_unverified_header(token)
    kid = headers['kid']
    
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
    
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(keys[key_index]))
    
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'], audience=os.environ['CLIENT_ID'])
    except jwt.ExpiredSignatureError:
        print('Token is expired')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
    except Exception as e:
        print(f'Unable to parse token: {str(e)}')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
    
    principal_id = payload['sub']
    user_groups = payload.get('cognito:groups', [])

    method_arn = event['methodArn']
    
    if 'Admin' in user_groups:
        effect = 'Allow'
    else:
        effect = 'Deny'
    
    policy = generate_policy(principal_id, effect, method_arn)
    
    return policy

def generate_policy(principal_id, effect, method_arn):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': method_arn
            }]
        }
    }