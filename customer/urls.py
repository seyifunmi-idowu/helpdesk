from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='customer_dashboard'),
    path('create-ticket/', views.create_ticket_public, name='create_ticket_public'),
    # path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),

    # Public Knowledge Base URLs (Customer App)
    path('search/', views.public_search_results, name='search'),
    path('folder/<int:folder_id>/', views.public_folder_detail, name='folder_detail'),
    path('folder/<int:folder_id>/articles/', views.public_folder_articles, name='folder_articles'),
    path('folder/<int:folder_id>/category/<int:category_id>/', views.public_category_detail, name='category_detail'),
    path('article/<slug:article_slug>/', views.public_article_detail, name='article_detail'),

    # Customer app URLs will go here

    # Authenticated Customer URLs
    path('dashboard/', views.authenticated_customer_dashboard, name='authenticated_customer_dashboard'),
    path('tickets/', views.customer_ticket_list, name='customer_ticket_list'),
    path('tickets/<int:ticket_id>/', views.customer_view_ticket, name='customer_view_ticket'),
    path('create-ticket-auth/', views.create_ticket_authenticated, name='create_ticket_authenticated'),
    path('profile/', views.customer_profile, name='customer_profile'),
]
