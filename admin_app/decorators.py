# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required

# def staff_required(view_func):
#     @login_required(login_url='/custom/adminlogin/')
#     def wrapper(request,*args,**kwargs):
#         if request.user.is_staff:
#             return view_func(request,*args,**kwargs)
#         return redirect("signin")
#     return wrapper