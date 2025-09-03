from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/update_status/', views.update_ticket_status, name='update_ticket_status'),
    path('tickets/<int:ticket_id>/update_priority/', views.update_ticket_priority, name='update_ticket_priority'),
    path('tickets/<int:ticket_id>/update_agent/', views.update_ticket_agent, name='update_ticket_agent'),
    path('tickets/<int:ticket_id>/update_type/', views.update_ticket_type, name='update_ticket_type'),
    path('tickets/<int:ticket_id>/update_group/', views.update_ticket_group, name='update_ticket_group'),
    path('tickets/<int:ticket_id>/update_team/', views.update_ticket_team, name='update_ticket_team'),
    path('tickets/<int:ticket_id>/', views.ticket_view, name='ticket_view'),
    path('workflows/', views.workflow_list, name='workflow_list'),
    path('workflows/create/', views.workflow_create, name='workflow_create'),
    path('workflows/<int:workflow_id>/edit/', views.workflow_edit, name='workflow_edit'),
    path('workflows/<int:workflow_id>/delete/', views.workflow_delete, name='workflow_delete'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),

    # Ticket Types
    path('ticket-types/', views.ticket_type_list, name='ticket_type_list'),
    path('ticket-types/create/', views.ticket_type_create, name='ticket_type_create'),
    path('ticket-types/<int:ticket_type_id>/edit/', views.ticket_type_edit, name='ticket_type_edit'),
    path('ticket-types/<int:ticket_type_id>/delete/', views.ticket_type_delete, name='ticket_type_delete'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),

    # Saved Replies
    path('saved-replies/', views.saved_reply_list, name='saved_reply_list'),
    path('saved-replies/create/', views.saved_reply_create, name='saved_reply_create'),
    path('saved-replies/<int:saved_reply_id>/edit/', views.saved_reply_edit, name='saved_reply_edit'),
    path('saved-replies/<int:saved_reply_id>/delete/', views.saved_reply_delete, name='saved_reply_delete'),

    # Prepared Responses
    path('prepared-responses/', views.prepared_response_list, name='prepared_response_list'),
    path('prepared-responses/create/', views.prepared_response_create, name='prepared_response_create'),
    path('prepared-responses/<int:prepared_response_id>/edit/', views.prepared_response_edit, name='prepared_response_edit'),
    path('prepared-responses/<int:prepared_response_id>/delete/', views.prepared_response_delete, name='prepared_response_delete'),

    # API endpoints
    path('api/tickets/', views.get_filtered_tickets_and_counts, name='get_filtered_tickets_and_counts'),
    path('api/agents/', views.get_agents, name='get_agents'),
    path('api/groups/', views.get_groups, name='get_groups'),
    path('api/teams/', views.get_teams, name='get_teams'),
    path('api/tags/', views.get_tags, name='get_tags'),
    path('api/ticket-types/', views.get_ticket_types, name='get_ticket_types'),
    path('api/priorities/', views.get_priorities, name='get_priorities'),
    path('api/statuses/', views.get_statuses, name='get_statuses'),
    path('api/email-templates/', views.get_email_templates, name='get_email_templates'),
]
