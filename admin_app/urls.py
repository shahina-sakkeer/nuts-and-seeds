from django.urls import path
from . import views

urlpatterns=[
    path("dashboard/",views.admin_dashboard,name="dashboard_home"),
    path("login/",views.admin_login,name="admin_signin")
]