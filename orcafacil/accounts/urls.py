# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('upgrade/', views.upgrade_plan, name='upgrade'),
    path("edit_access",views.edit_access,name='edit_access'),
    path("edit_profile",views.edit_profile,name='edit_profile'),
    path("edit_company",views.edit_company,name='edit_company'),

    

]
