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

    path('dashboard/budget/view/<int:budget_id>/',views.budget_view,name="budget_view"),

    path('dashboard/budget/edit/<int:budget_id>/',views.budget_edit,name="budget_edit"),

    path('dashboard/budget/delete/<int:budget_id>',views.budget_delete, name='budget_delete'),
    path('budget/<int:pk>/view_pdf/', views.view_report, name='view_pdf'),
    path('budget/<int:pk>/pdf/', views.download_report, name='budget_pdf'),

    

]