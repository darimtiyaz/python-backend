from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .services import AuthService
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.contrib.auth.models import AnonymousUser

class SignUpView(APIView):
    def post(self, request):
        print("request data ", request.data)
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            auth_service = AuthService()
            
            # Check if user already exists
            if auth_service.get_user_by_email(serializer.validated_data['email']):
                return Response({'error': 'User with this email already exists'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = auth_service.create_user(serializer.validated_data)
            
            # Generate JWT token
            token = auth_service.create_token(user)
            
            # Create response with token in cookies
            response = Response(
                {'message': 'User created successfully'}, 
                status=status.HTTP_201_CREATED
            )
            
            # Set token in HTTP-only cookie
            response.set_cookie(
                key='access_token',
                value=token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7*24*60*60
            )
            
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignInView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            auth_service = AuthService()
            user, error = auth_service.authenticate_user(
                serializer.validated_data['email'],
                serializer.validated_data['password']
            )
            
            if error:
                return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT token
            token = auth_service.create_token(user)
            
            # Create response with token in cookies
            response = Response(
                {'message': 'Login successful'}, 
                status=status.HTTP_200_OK
            )
            
            # Set token in HTTP-only cookie
            response.set_cookie(
                key='access_token',
                value=token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7*24*60*60
            )
            
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignOutView(APIView):
    def post(self, request):
        response = Response({'message': 'Logged out successfully'})
        response.delete_cookie('access_token')
        return response

class MeView(APIView):
    def get(self, request):
        if not request.auth_user:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserProfileSerializer(request.auth_user)
        return Response(serializer.data)
    # Add this to prevent POST requests to this endpoint
    def post(self, request):
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            auth_service = AuthService()
            reset_token, error = auth_service.initiate_password_reset(
                serializer.validated_data['email']
            )
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            # In a production environment, send an email here
            # send_mail = auth_service.send_reset_email(serializer.validated_data['email'], reset_token)
            # For development,  return the token in the response
            return Response({
                'message': 'Password reset initiated check the mail',
                'reset_token': reset_token  # Remove this in production
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            auth_service = AuthService()
            success, error = auth_service.reset_password(
                serializer.validated_data['email'],
                serializer.validated_data['token'],
                serializer.validated_data['new_password']
            )
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetTokenView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # need email and token for verification
            auth_service = AuthService()
            
            # Check if token is valid
            user = auth_service.get_user_by_email(serializer.validated_data['email'])
            if user and user.reset_token == serializer.validated_data['token'] and user.reset_token_expiry:
                from django.utils import timezone
                if user.reset_token_expiry > timezone.now():
                    return Response({
                        'message': 'Token is valid'
                    }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)