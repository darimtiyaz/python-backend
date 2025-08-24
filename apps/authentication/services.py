import bcrypt
from .repositories.user_repository import UserRepository
import uuid
from django.core.mail import send_mail
from django.conf import settings
from utils.jwt_utils import create_jwt_token, verify_jwt_token


from utils.jwt_utils import create_jwt_token, verify_jwt_token

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_user_by_id(self, user_id):
        return self.user_repository.get_user_by_id(user_id)
    
    def get_user_by_email(self, email):
        return self.user_repository.get_user_by_email(email)
    
    def create_user(self, user_data):
        return self.user_repository.create_user(user_data)
    
    def authenticate_user(self, email, password):
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user, None
        return None, 'Invalid credentials'
    
    def create_token(self, user):
        user_id = str(user.id)
        return create_jwt_token(user_id)
    
    def verify_token(self, token):
        return verify_jwt_token(token)

    def generate_reset_token(self):
        return str(uuid.uuid4())
    
    def initiate_password_reset(self, email):
        user = self.get_user_by_email(email)
        if not user:
            return None, 'User not found'
        
        # Generate reset token
        reset_token = self.generate_reset_token()
        
        # Save token to database
        if self.user_repository.set_password_reset_token(email, reset_token):
            return reset_token, None
        
        return None, 'Failed to generate reset token'
    
    def reset_password(self, email, token, new_password):
        # Verify the reset token
        if not self.user_repository.verify_reset_token(email, token):
            return False, 'Invalid or expired reset token'
        
        # Update the password
        user = self.get_user_by_email(email)
        if user:
            user.set_password(new_password)
            user.save()
            
            # Clear the reset token
            self.user_repository.clear_reset_token(email)
            return True, None
        
        return False, 'User not found'
    
    # Optional: Email sending function (you can implement this later)
    def send_reset_email(self, email, reset_token):
        reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}&email={email}"
        
        subject = "Password Reset Request"
        message = f"Click the link to reset your password: {reset_url}"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(subject, message, from_email, [email])
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
