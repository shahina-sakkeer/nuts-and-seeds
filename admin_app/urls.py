from django.urls import path
from . import views

urlpatterns=[
    path("dashboard/",views.admin_dashboard,name="dashboard_home"),
    path("login/",views.admin_login,name="admin_signin"),
    path("category/add/",views.add_category,name="addCategory"),
    path("categories/",views.list_category,name="listCategory"),
    path("category/edit/<int:id>",views.edit_category,name="editCategory"),
    path("category/delete/<int:id>",views.delete_category,name="deleteCategory"),
    path("products/",views.products,name="listProduct"),
    path("product/add/",views.add_products,name="addProduct"),
    path("product/edit/<int:id>",views.edit_product,name="editProduct"),
    path("product/delete/<int:id>",views.soft_delete_product,name="deleteProduct"),
    path("search/",views.search,name="searching"),
    path("search/category",views.searchCategory,name="category_search"),
    path('customers/',views.customer,name="users"),
    path("block-button/<int:id>",views.blockUser,name="blockCustomer"),
    path("logout/",views.signout,name="admin_signout")
]