
from django.contrib import admin
from .models import Post, Comment
from ckeditor.widgets import CKEditorWidget
from django import forms

class PostAdminForm(forms.ModelForm):
	content = forms.CharField(widget=CKEditorWidget())

	class Meta:
		model = Post
		fields = '__all__'

class PostAdmin(admin.ModelAdmin):
	form = PostAdminForm

class CommentAdmin(admin.ModelAdmin):
	list_display = ['name', 'post', 'created_at']
	list_filter = ['created_at', 'post']
	search_fields = ['name', 'content']

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
