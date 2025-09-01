from django.db import models
from authentication.models import SupportGroup, UserInstance
from ticket.models import Tag


class Folder(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    visibility = models.CharField(max_length=255, default='public')  # public, private, authenticated
    sort_order = models.IntegerField(default=0)
    solution_image = models.ImageField(upload_to='folder_images/', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField('SolutionCategory', through='FolderCategory', related_name='folder_categories_reverse')

    class Meta:
        verbose_name = "Folder"
        verbose_name_plural = "Folders"
        db_table = "uv_solutions"

    def __str__(self):
        return self.name

    def count_categories(self):
        return self.categories.count()

    def count_articles(self):
        return Article.objects.filter(categories__in=self.categories.all()).distinct().count()


class SolutionCategory(models.Model):
    SORTING_CHOICES = [
        ('ascending', 'Ascending'),
        ('descending', 'Descending'),
    ]

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    sorting = models.CharField(max_length=20, choices=SORTING_CHOICES, default='ascending')
    status = models.BooleanField(default=True)  # Active/Inactive
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    folders = models.ManyToManyField('Folder', through='FolderCategory', related_name='categories_through_category')

    class Meta:
        verbose_name = "Solution Category"
        verbose_name_plural = "Solution Categories"
        db_table = "uv_solution_category"

    def __str__(self):
        return self.name


class FolderCategory(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    category = models.ForeignKey(SolutionCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_solution_category_mapping"
        unique_together = ('folder', 'category')


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    meta_description = models.TextField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    viewed = models.IntegerField(default=0)
    stared = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField('SolutionCategory', through='ArticleCategory', related_name='articles')
    tags = models.ManyToManyField(Tag, through='ArticleTags', related_name='kb_articles')
    related_articles = models.ManyToManyField(
        'self',
        through='RelatedArticles',
        symmetrical=False,
        related_name='related_to',
        through_fields=('article', 'related_article')
    )

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        db_table = "uv_article"

    def __str__(self):
        return self.name


class ArticleCategory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    category = models.ForeignKey(SolutionCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_article_category"
        unique_together = ('article', 'category')


class ArticleHistory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(UserInstance, on_delete=models.SET_NULL, null=True,
                             blank=True)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article History"
        verbose_name_plural = "Article Histories"
        db_table = "uv_article_history"

    def __str__(self):
        return f"History for {self.article.name} on {self.date_added.strftime('%Y-%m-%d %H:%M')}"


class ArticleTags(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = "uv_article_tags"
        unique_together = ('article', 'tag')


class RelatedArticles(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='+')
    related_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='+')

    class Meta:
        db_table = "uv_related_articles"
        unique_together = ('article', 'related_article')


class ArticleFeedback(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(UserInstance, on_delete=models.SET_NULL, null=True,
                             blank=True)
    is_helpful = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article Feedback"
        verbose_name_plural = "Article Feedback"
        db_table = "uv_article_feedback"

    def __str__(self):
        return f"Feedback for {self.article.name} - Helpful: {self.is_helpful}"


class ArticleViewLog(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(UserInstance, on_delete=models.SET_NULL, null=True,
                             blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article View Log"
        verbose_name_plural = "Article View Logs"
        db_table = "uv_article_view_log"

    def __str__(self):
        return f"View of {self.article.name} by {self.user.email if self.user else 'Anonymous'} at {self.viewed_at}"


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    promo_text = models.TextField(null=True, blank=True)
    promo_tag = models.CharField(max_length=255, null=True, blank=True)
    tag_color = models.CharField(max_length=255, null=True, blank=True)
    link_text = models.CharField(max_length=255, null=True, blank=True)
    link_url = models.URLField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    group = models.ForeignKey(SupportGroup, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        db_table = "uv_announcement"

    def __str__(self):
        return self.title


class MarketingModule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='marketing_module_images/', null=True, blank=True)
    border_color = models.CharField(max_length=255, null=True, blank=True)
    link_url = models.URLField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    group = models.ForeignKey(SupportGroup, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Marketing Module"
        verbose_name_plural = "Marketing Modules"
        db_table = "uv_marketing_module"

    def __str__(self):
        return self.title