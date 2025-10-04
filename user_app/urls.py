from django.urls import path
from . import views

urlpatterns=[
    path("register/",views.register,name="signup"),
    path("verify/",views.verify_otp,name="verify_otp"),
    path("resend/",views.resend_otp,name="resend_otp"),
    path("login/",views.signin,name="signin"),
    path("home/",views.home_page,name="home"),
    path("forgot-password/",views.forgot_password,name="forgotpswd"),
    path("forgot-password-otp/",views.verify_forgot_otp,name="forgot_password_otp"),
    path("reset-password/",views.reset_password,name="reset_password")

]

