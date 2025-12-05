from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from .models import Post

# LISTAR
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

# DETALHE
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/post_details.html', {'post': post})

# CRIAR
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Post.objects.create(title=title, content=content)
        return redirect('posts:post_list')
    return render(request, 'posts/post_form.html')

# EDITAR
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()
        return redirect('posts:post_detail', pk=post.pk)
    return render(request, 'posts/post_form.html', {'post': post})

# DELETAR
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('posts:post_list')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})

