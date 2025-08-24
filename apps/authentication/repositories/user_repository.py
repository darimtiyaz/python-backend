from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
User = get_user_model()

class UserRepository:
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    def get_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    def create_user(self, user_data):
        return User.objects.create_user(**user_data)
    
    def update_user(self, user_id, user_data):
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in user_data.items():
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            user.save()
            return user
        return None
    
    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False

    def set_password_reset_token(self, email, token, expiry_minutes=30):
        user = self.get_user_by_email(email)
        if user:
            user.reset_token = token
            user.reset_token_expiry = timezone.now() + timedelta(minutes=expiry_minutes)
            user.save()
            return True
        return False
    
    def verify_reset_token(self, email, token):
        user = self.get_user_by_email(email)
        if user and user.reset_token == token and user.reset_token_expiry > timezone.now():
            return True
        return False
    
    def clear_reset_token(self, email):
        user = self.get_user_by_email(email)
        if user:
            user.reset_token = None
            user.reset_token_expiry = None
            user.save()
            return True
        return False