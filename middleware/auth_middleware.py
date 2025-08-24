from django.utils.deprecation import MiddlewareMixin
from apps.authentication.services import AuthService
from django.contrib.auth.models import AnonymousUser

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for auth endpoints
        auth_paths = ['/api/auth/signin', '/api/auth/signin/', 
                     '/api/auth/signup', '/api/auth/signup/']
        
        if any(request.path.startswith(path) for path in auth_paths):
            return None
        
        # Get token from cookie     
        token = request.COOKIES.get('access_token')
        print(f"Token from cookie: {token}")
        
        if token:
            auth_service = AuthService()
            user_id = auth_service.verify_token(token)
            print("user id ", user_id)
            
            if user_id:
                user = auth_service.get_user_by_id(user_id)
                print("user ", user)
                if user:
                    request.auth_user = user
                    return None
        
        # If no valid token, set user to Anonymous
        request.auth_user = AnonymousUser() 
        return None