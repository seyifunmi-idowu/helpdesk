from django.urls import path
from . import views

urlpatterns = [
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/create/', views.folder_create_edit, name='folder_create'),
    path('folders/<int:pk>/edit/', views.folder_create_edit, name='folder_edit'),
    path('folders/<int:pk>/delete/', views.folder_delete, name='folder_delete'),

    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create_edit, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_create_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create_edit, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_create_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('api/articles/search/', views.article_search_api, name='article_search_api'),
    path('api/articles/<int:article_id>/related/', views.get_related_articles_api, name='get_related_articles_api'),
    path('api/articles/<int:article_id>/related/add/', views.add_related_article_api, name='add_related_article_api'),
    path('api/articles/<int:article_id>/related/remove/', views.remove_related_article_api, name='remove_related_article_api'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create_edit, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_create_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('marketing-modules/', views.marketing_module_list, name='marketing_module_list'),
    path('marketing-modules/create/', views.marketing_module_create_edit, name='marketing_module_create'),
    path('marketing-modules/<int:pk>/edit/', views.marketing_module_create_edit, name='marketing_module_edit'),
    path('marketing-modules/<int:pk>/delete/', views.marketing_module_delete, name='marketing_module_delete'),
]
