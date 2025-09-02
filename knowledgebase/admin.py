from django.contrib import admin
from .models import (
    Folder, SolutionCategory, FolderCategory, Article, ArticleCategory, 
    ArticleHistory, ArticleTags, RelatedArticles, ArticleFeedback, 
    ArticleViewLog, Announcement, MarketingModule
)

admin.site.register(Folder)
admin.site.register(SolutionCategory)
admin.site.register(FolderCategory)
admin.site.register(Article)
admin.site.register(ArticleCategory)
admin.site.register(ArticleHistory)
admin.site.register(ArticleTags)
admin.site.register(RelatedArticles)
admin.site.register(ArticleFeedback)
admin.site.register(ArticleViewLog)
admin.site.register(Announcement)
admin.site.register(MarketingModule)
