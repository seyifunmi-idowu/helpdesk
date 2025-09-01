from django.urls import path
from . import views

urlpatterns = [
    path('branding/', views.branding_settings_view, name='branding_settings'),
    path('spam/', views.spam_settings_view, name='spam_settings'),
    path('email-templates/', views.email_template_list, name='email_template_list'),
    path('email-templates/create/', views.email_template_create, name='email_template_create'),
    path('email-templates/<int:pk>/edit/', views.email_template_edit, name='email_template_edit'),
    path('email-templates/<int:pk>/delete/', views.email_template_delete, name='email_template_delete'),
]