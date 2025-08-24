from django.urls import path
from .views import SignUpView, SignInView, SignOutView, MeView, ForgotPasswordView, ResetPasswordView, VerifyResetTokenView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', SignOutView.as_view(), name='signout'),
    path('me/', MeView.as_view(), name='me'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify-reset-token/', VerifyResetTokenView.as_view(), name='verify_reset_token'),
]