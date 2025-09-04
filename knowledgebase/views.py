from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Q
from django.http import JsonResponse
from .models import Announcement, Article, SolutionCategory, MarketingModule, Folder
from .forms import AnnouncementForm, MarketingModuleForm, FolderForm, CategoryForm, ArticleForm
from authentication.models import SupportGroup
from ticket.models import Tag
import json
from authentication.decorators import admin_login_required, permission_required

# Announcement Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
def announcement_list(request):
    announcements = Announcement.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        announcements = announcements.filter(Q(title__icontains=search_query) | Q(promo_text__icontains=search_query))

    # Filter by is_active
    is_active_filter = request.GET.get('is_active')
    if is_active_filter == 'true':
        announcements = announcements.filter(is_active=True)
    elif is_active_filter == 'false':
        announcements = announcements.filter(is_active=False)

    # Filter by group
    group_filter = request.GET.get('group')
    if group_filter:
        announcements = announcements.filter(group__id=group_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'title') # Default sort by title
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    announcements = announcements.order_by(sort_by)

    # Get all support groups for the filter dropdown
    support_groups = SupportGroup.objects.all()

    context = {
        "view": "Announcements",
        "user": request.user,
        "announcements": announcements,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "is_active_filter": is_active_filter,
        "group_filter": group_filter,
        "support_groups": support_groups,
    }
    return render(request, "announcement_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
def announcement_create_edit(request, pk=None):
    if pk:
        announcement = get_object_or_404(Announcement, pk=pk)
        form = AnnouncementForm(instance=announcement)
        view = "Edit Announcement"
    else:
        announcement = None
        form = AnnouncementForm()
        view = "Create Announcement"

    if request.method == 'POST':
        if pk:
            form = AnnouncementForm(request.POST, instance=announcement)
        else:
            form = AnnouncementForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('announcement_list')

    context = {
        'form': form,
        'view': view,
        'user': request.user,
    }
    return render(request, 'announcement_create_edit.html', context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
@require_POST
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    return redirect('announcement_list')

# Marketing Module Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
def marketing_module_list(request):
    marketing_modules = MarketingModule.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        marketing_modules = marketing_modules.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # Filter by is_active
    is_active_filter = request.GET.get('is_active')
    if is_active_filter == 'true':
        marketing_modules = marketing_modules.filter(is_active=True)
    elif is_active_filter == 'false':
        marketing_modules = marketing_modules.filter(is_active=False)

    # Filter by group
    group_filter = request.GET.get('group')
    if group_filter:
        marketing_modules = marketing_modules.filter(group__id=group_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'title') # Default sort by title
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    marketing_modules = marketing_modules.order_by(sort_by)

    # Get all support groups for the filter dropdown
    support_groups = SupportGroup.objects.all()

    context = {
        "view": "Marketing Modules",
        "user": request.user,
        "marketing_modules": marketing_modules,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "is_active_filter": is_active_filter,
        "group_filter": group_filter,
        "support_groups": support_groups,
    }
    return render(request, "marketing_module_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
def marketing_module_create_edit(request, pk=None):
    if pk:
        module = get_object_or_404(MarketingModule, pk=pk)
        form = MarketingModuleForm(request.POST or None, request.FILES or None, instance=module)
        view = "Edit Marketing Module"
    else:
        module = None
        form = MarketingModuleForm(request.POST or None, request.FILES or None)
        view = "Create Marketing Module"

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('marketing_module_list')

    context = {
        'form': form,
        'view': view,
        'user': request.user,
    }
    return render(request, 'marketing_module_create_edit.html', context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_MARKETING_ANNOUNCEMENT')
@require_POST
def marketing_module_delete(request, pk):
    module = get_object_or_404(MarketingModule, pk=pk)
    module.delete()
    return redirect('marketing_module_list')

# Folder Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def folder_list(request):
    folders = Folder.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        folders = folders.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Filter by visibility
    visibility_filter = request.GET.get('visibility')
    if visibility_filter:
        folders = folders.filter(visibility=visibility_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    folders = folders.order_by(sort_by)

    context = {
        "view": "Folders",
        "user": request.user,
        "folders": folders,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "visibility_filter": visibility_filter,
    }
    return render(request, "folder_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def folder_create_edit(request, pk=None):
    if pk:
        folder = get_object_or_404(Folder, pk=pk)
        form = FolderForm(request.POST or None, request.FILES or None, instance=folder)
        view = "Edit Folder"
    else:
        folder = None
        form = FolderForm(request.POST or None, request.FILES or None)
        view = "Create Folder"

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('folder_list')

    context = {
        'form': form,
        'view': view,
        'user': request.user,
    }
    return render(request, 'folder_create_edit.html', context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_POST
def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk)
    folder.delete()
    return redirect('folder_list')

# Category Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def category_list(request):
    categories = SolutionCategory.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'true':
        categories = categories.filter(status=True)
    elif status_filter == 'false':
        categories = categories.filter(status=False)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    categories = categories.order_by(sort_by)

    context = {
        "view": "Categories",
        "user": request.user,
        "categories": categories,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "status_filter": status_filter,
    }
    return render(request, "category_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def category_create_edit(request, pk=None):
    category = None
    if pk:
        category = get_object_or_404(SolutionCategory, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            form.save_m2m() # Save many-to-many data
            return redirect('category_list')
    else: # GET request
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'view': "Edit Category" if pk else "Create Category",
        'user': request.user,
    }
    return render(request, 'category_create_edit.html', context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(SolutionCategory, pk=pk)
    category.delete()
    return redirect('category_list')

# Article Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def article_list(request):
    articles = Article.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        articles = articles.filter(
            Q(name__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(meta_description__icontains=search_query) |
            Q(meta_title__icontains=search_query) |
            Q(keywords__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        articles = articles.filter(status=status_filter)

    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        articles = articles.filter(articlecategory__category__id=category_filter)

    # Filter by tag
    tag_filter = request.GET.get('tag')
    if tag_filter:
        articles = articles.filter(articletags__tag__id=tag_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    articles = articles.order_by(sort_by)

    # Get all categories and tags for the filter dropdowns
    categories = SolutionCategory.objects.all()
    tags = Tag.objects.all()

    context = {
        "view": "Articles",
        "user": request.user,
        "articles": articles,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "status_filter": status_filter,
        "category_filter": category_filter,
        "tag_filter": tag_filter,
        "categories": categories,
        "tags": tags,
        "STATUS_CHOICES": Article.STATUS_CHOICES,
    }
    return render(request, "article_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def article_create_edit(request, pk=None):
    if pk:
        article = get_object_or_404(Article, pk=pk)
        form = ArticleForm(request.POST or None, instance=article)
        view = "Edit Article"
    else:
        article = None
        form = ArticleForm(request.POST or None)
        view = "Create Article"

    if request.method == 'POST':
        if form.is_valid():
            article = form.save(commit=False)
            article.save()
            form.save_m2m() # Save many-to-many data
            return redirect('article_list')

    context = {
        'form': form,
        'view': view,
        'user': request.user,
        'article': article,
    }
    return render(request, 'article_create_edit.html', context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_POST
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return redirect('article_list')

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
def article_search_api(request):
    query = request.GET.get('q', '')
    articles = Article.objects.filter(name__icontains=query).values('id', 'name')[:10] # Limit to 10 results
    return JsonResponse(list(articles), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_http_methods(["GET"])
def get_related_articles_api(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    related_articles = article.related_articles.all().values('id', 'name')
    return JsonResponse(list(related_articles), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_http_methods(["POST"])
def add_related_article_api(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    try:
        data = json.loads(request.body)
        related_article_id = data.get('related_article_id')
        if not related_article_id:
            return JsonResponse({'error': 'related_article_id is required'}, status=400)

        related_article = get_object_or_404(Article, pk=related_article_id)
        article.related_articles.add(related_article)
        return JsonResponse({'status': 'success', 'message': 'Related article added.'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_KNOWLEDGEBASE')
@require_http_methods(["POST"])
def remove_related_article_api(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    try:
        data = json.loads(request.body)
        related_article_id = data.get('related_article_id')
        if not related_article_id:
            return JsonResponse({'error': 'related_article_id is required'}, status=400)

        related_article = get_object_or_404(Article, pk=related_article_id)
        article.related_articles.remove(related_article)
        return JsonResponse({'status': 'success', 'message': 'Related article removed.'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
