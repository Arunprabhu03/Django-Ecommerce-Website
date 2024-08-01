
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('category/<str:foo>',views.category,name='category'),
    path('category_summary/',views.category_summary,name='category_summary'),
    path('product/<int:pk>',views.product,name='product'),
    path('register/',views.register_user,name='register'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('about/',views.about,name='about'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_info/', views.update_info, name='update_info'),
    path('search/', views.search, name='search'),
    
    
    path('add-category/', views.add_category, name='add_category'), 
    path('add-product/', views.add_product, name='add_product'),
    
    path('update-product/<int:pk>/', views.update_product, name='update_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
]
