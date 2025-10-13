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
    path("reset-password/",views.reset_password,name="reset_password"),
    path("logout/",views.signout,name="signout"),
    path("landing-page/",views.landing,name="landing_page"),
    path("category/<int:id>/products/",views.products_by_category,name="products_on_category"),
    path("products/",views.list_products,name="all_products"),
    path("products/filter/<int:id>/",views.filterProducts,name="filtering"),
    path("products/filter/",views.filterProducts,name="filtering"),
    path("products/<int:id>/",views.productDetail,name="product_details"),
    path("variant/<int:id>/price/",views.weightFilter,name="weight_price")

]

