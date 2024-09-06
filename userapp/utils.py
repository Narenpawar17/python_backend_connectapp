from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


def custom_response(success, data=None, error=None, status_code=status.HTTP_200_OK):
    if success:
        return Response({
            'success': True,
            'data': data
        }, status=status_code)
    else:
        return Response({
            'success': False,
            'error': error
        }, status=status_code)


def decode_token(request):
    # Extract the token from the Authorization header
    print(request.headers.get('Authorization', None), "auth header")
    auth_header = request.headers.get('Authorization', None)
    
    if not auth_header or not auth_header.startswith('Bearer '):
        print("Authorization header missing or does not start with 'Bearer'.")
        return None
    token = auth_header.split(' ')[1]
    
    print(token)
    try:
        # Decode the token using AccessToken
        decoded_token = AccessToken(token)
        print(decode_token, " skjfhkjAFB")
        payload = decoded_token.payload
        return payload
    except InvalidToken:
        print("Invalid token.")
        return None
    except TokenError as e:
        print(f"Token error: {e}")
        return None
    except ValueError as e:
        print(f"Value error: {e}")
        return None