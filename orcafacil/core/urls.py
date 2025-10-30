from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('dashboard/<str:section>/', views.dashboard_content, name='dashboard_content'),
    
    path('clients/', views.client_list, name='client_list'),
    
    path('clients/new/', views.client_create, name='client_create'),

    path('client/delete/<int:client_id>',views.delete_client,name='delete_client'),

    path('dashboard/client/view/<int:client_id>/',views.client_view,name='client_view'),

    path('dashboard/client/edit/<int:client_id>/',views.client_edit,name='client_edit'),
    

    path('budgets/', views.budgets, name='budget'),
    
    path('budgets/new/', views.budget_create, name='budget_create'),
]