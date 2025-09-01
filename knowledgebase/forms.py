from django import forms
from .models import Announcement, MarketingModule, Folder, SolutionCategory, Article
from authentication.models import SupportGroup
from ticket.models import Tag

class AnnouncementForm(forms.ModelForm):
    PROMO_TAG_CHOICES = [
        ('', 'Choose a promo tag'),
        ('New', 'New'),
        ('Offer', 'Offer'),
        ('Update', 'Update'),
    ]

    STATUS_CHOICES = [
        (True, 'Publish'),
        (False, 'Draft'),
    ]

    promo_tag = forms.ChoiceField(choices=PROMO_TAG_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    tag_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-control', 'style': 'width: 100px;'}), required=False)
    is_active = forms.TypedChoiceField(choices=STATUS_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    group = forms.ModelChoiceField(queryset=SupportGroup.objects.all(), required=False, empty_label="Choose a group", widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))

    class Meta:
        model = Announcement
        fields = ['title', 'promo_text', 'promo_tag', 'tag_color', 'link_text', 'link_url', 'is_active', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'promo_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 50%;'}),
            'link_text': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'link_url': forms.URLInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
        }

class MarketingModuleForm(forms.ModelForm):
    STATUS_CHOICES = [
        (True, 'Publish'),
        (False, 'Draft'),
    ]

    border_color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-control', 'style': 'width: 100px;'}), required=False)
    is_active = forms.TypedChoiceField(choices=STATUS_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    group = forms.ModelChoiceField(queryset=SupportGroup.objects.all(), required=False, empty_label="Choose a group", widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))

    class Meta:
        model = MarketingModule
        fields = ['title', 'description', 'border_color', 'link_url', 'image', 'is_active', 'group']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 50%;'}),
            'link_url': forms.URLInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class FolderForm(forms.ModelForm):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('authenticated', 'Authenticated'),
    ]

    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))

    class Meta:
        model = Folder
        fields = ['name', 'description', 'visibility', 'solution_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 50%;'}),
            'solution_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class CategoryForm(forms.ModelForm):
    STATUS_CHOICES = [
        (True, 'Publish'),
        (False, 'Draft'),
    ]

    SORTING_CHOICES = [
        ('ascending', 'Ascending Order (A-Z)'),
        ('descending', 'Descending Order (Z-A)'),
    ]

    status = forms.TypedChoiceField(choices=STATUS_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    sorting = forms.ChoiceField(choices=SORTING_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    folders = forms.ModelMultipleChoiceField(queryset=Folder.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'width: 50%;'}))

    class Meta:
        model = SolutionCategory
        fields = ['name', 'description', 'folders', 'sort_order', 'sorting', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 50%;'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
        }

class ArticleForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    categories = forms.ModelMultipleChoiceField(queryset=SolutionCategory.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    stared = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = Article
        fields = ['name', 'content', 'categories', 'status', 'stared', 'tags', 'slug', 'meta_title', 'meta_description', 'keywords']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'content': forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 10}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'width: 50%;'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
        }
