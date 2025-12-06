from django import forms
from .models import Post, Comment
from ckeditor.widgets import CKEditorWidget

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'comment-name', 'placeholder': 'Seu nome'}),
            'content': forms.Textarea(attrs={'class': 'comment-text', 'placeholder': 'Seu comentário', 'rows': 4})
        }
