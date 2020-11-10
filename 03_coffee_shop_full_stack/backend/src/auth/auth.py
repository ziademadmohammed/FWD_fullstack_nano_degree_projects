from os import environ
import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-6icr1d00.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeshop'

# AuthError Exception

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():

    authHeader = request.headers.get("Authorization", None)

    if not authHeader:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    headerParts = authHeader.split(' ')

    if len(headerParts) != 2 or not headerParts:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be in the format'
            ' Bearer token'}, 401)

    elif headerParts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with Bearer'}, 401)

    return headerParts[1]

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission Not found',
        }, 401)

    return True

def verify_decode_jwt(token):
    # Get public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # data in the header
    unverifiedHeader = jwt.get_unverified_header(token)

    # Auth0 token should have a key id
    if 'kid' not in unverifiedHeader:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)

    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == unverifiedHeader['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break

    # verify the token
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload

        except jwt.ExpiredSignatureError:

            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:

            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, '
                'check the audience and issuer.'
            }, 401)

        except Exception:

            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 401)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator