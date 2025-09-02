from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Privileges
    path('privileges/', views.privilege_list, name='privilege_list'),
    path('privileges/create/', views.privilege_create, name='privilege_create'),
    path('privileges/<int:privilege_id>/edit/', views.privilege_edit, name='privilege_edit'),
    path('privileges/<int:privilege_id>/delete/', views.privilege_delete, name='privilege_delete'),

    # Groups
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # Teams
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),


    # Agents
    path('agents/', views.agent_list, name='agent_list'),
    path('agents/invite/', views.agent_invite, name='agent_invite'),
    path('agents/create/', views.create_agent, name='create_agent'),
    path('agents/<int:agent_id>/edit/', views.agent_edit, name='agent_edit'),
    path('agents/<int:agent_id>/delete/', views.agent_delete, name='agent_delete'),

    # Password reset links (built-in)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
]

