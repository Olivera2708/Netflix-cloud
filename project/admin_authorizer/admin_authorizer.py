import jwt
import jwt.algorithms as alg
import json
import urllib.request
import os
from base64 import urlsafe_b64decode

def admin_authorizer(event, context):
    token = event['headers']['Authorization'].split()[1]
    user_pool_id = os.environ['USER_POOL_ID']
    
    # Parse JWT token without using get_unverified_header
    header_b64 = token.split('.')[0]
    header = json.loads(urlsafe_b64decode(header_b64 + '=' * (-len(header_b64) % 4)).decode('utf-8'))
    kid = header['kid']

    
    # Download JWKS
    keys_url = f"https://cognito-idp.eu-central-1.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode('utf-8'))['keys']

    # Find key
    key = next((k for k in keys if k['kid'] == kid), None)
    if key is None:
        print('Public key not found in jwks.json')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }

    # Convert key to RSA public key
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

    try:
        # Validate token
        payload = jwt.decode(token, public_key, algorithms=['RS256'], audience=os.environ['CLIENT_ID'])
    except jwt.ExpiredSignatureError:
        print('Token is expired')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }
    except jwt.JWTClaimsError:
        print('Token claims are invalid')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }
    except Exception as e:
        print(f'Unable to parse token: {str(e)}')
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
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
