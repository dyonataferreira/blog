
from django.contrib import admin
from .models import Post, Comment, Category
from ckeditor.widgets import CKEditorWidget
from django import forms

class PostAdminForm(forms.ModelForm):
	content = forms.CharField(widget=CKEditorWidget())

	class Meta:
		model = Post
		fields = '__all__'

class PostAdmin(admin.ModelAdmin):
	form = PostAdminForm
	list_display = ['title', 'category', 'created_at']
	list_filter = ['category', 'created_at']
	search_fields = ['title', 'content']

class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name', 'slug']
	search_fields = ['name']
	prepopulated_fields = {'slug': ('name',)}

class CommentAdmin(admin.ModelAdmin):
	list_display = ['name', 'post', 'created_at']
	list_filter = ['created_at', 'post']
	search_fields = ['name', 'content']

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
