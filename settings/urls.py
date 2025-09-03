from django.urls import path
from . import views

urlpatterns = [
    path('branding/', views.branding_settings_view, name='branding_settings'),
    path('spam/', views.spam_settings_view, name='spam_settings'),
    path('email-templates/', views.email_template_list, name='email_template_list'),
    path('email-templates/create/', views.email_template_create, name='email_template_create'),
    path('email-templates/<int:pk>/edit/', views.email_template_edit, name='email_template_edit'),
    path('email-templates/<int:pk>/delete/', views.email_template_delete, name='email_template_delete'),

    path('swiftmailers/', views.uv_swiftmailer_list, name='uv_swiftmailer_list'),
    path('swiftmailers/create/', views.uv_swiftmailer_create, name='uv_swiftmailer_create'),
    path('swiftmailers/<int:pk>/edit/', views.uv_swiftmailer_edit, name='uv_swiftmailer_edit'),
    path('swiftmailers/<int:pk>/delete/', views.uv_swiftmailer_delete, name='uv_swiftmailer_delete'),

    path('mailboxes/', views.uv_mailbox_list, name='uv_mailbox_list'),
    path('mailboxes/create/', views.uv_mailbox_create, name='uv_mailbox_create'),
    path('mailboxes/<int:pk>/edit/', views.uv_mailbox_edit, name='uv_mailbox_edit'),
    path('mailboxes/<int:pk>/delete/', views.uv_mailbox_delete, name='uv_mailbox_delete'),

    path('email-settings/', views.uv_email_settings_view, name='uv_email_settings_view'),
    path('swiftmailers/test-connection/', views.test_swiftmailer_connection, name='test_swiftmailer_connection'),
    path('mailboxes/test-connection/', views.test_mailbox_connection, name='test_mailbox_connection'),
]