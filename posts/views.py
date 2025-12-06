from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

# LISTAR
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    # extrair imagem de preview do conteúdo (primeira <img src=...>)
    import re
    posts_with_preview = []
    img_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', flags=re.IGNORECASE)
    media_re = re.compile(r'(?:https?:)?//[^/]+(/media/[^"\'\s>]+)|(/media/[^"\'\s>]+)')
    for p in posts:
        preview = None
        if p.content:
            m = img_re.search(p.content)
            if m:
                preview = m.group(1)
            else:
                # procurar referência direta a /media/arquivo
                m2 = media_re.search(p.content)
                if m2:
                    preview = m2.group(1) or m2.group(2)
        posts_with_preview.append({'post': p, 'thumb': preview})
    return render(request, 'posts/post_list.html', {'posts_with_preview': posts_with_preview})

# DETALHE
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    form = CommentForm()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('posts:post_detail', pk=post.pk)
    
    return render(request, 'posts/post_details.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

# CRIAR
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('posts:post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})

# EDITAR
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form, 'post': post})

# DELETAR
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('posts:post_list')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@require_POST
def upload_image(request):
    """Recebe um arquivo (campo 'image') e salva em MEDIA_ROOT/uploads/, retornando a URL."""
    upload = request.FILES.get('image')
    if not upload:
        return JsonResponse({'error': 'Nenhum arquivo enviado.'}, status=400)

    upload_dir = 'uploads'
    # cria um caminho disponível e salva o arquivo
    filename = default_storage.get_available_name(os.path.join(upload_dir, upload.name))
    saved_path = default_storage.save(filename, ContentFile(upload.read()))
    # Retornar URL absoluta para evitar problemas de acesso no cliente
    relative_url = settings.MEDIA_URL + saved_path.replace('\\', '/')
    try:
        absolute_url = request.build_absolute_uri(relative_url)
    except Exception:
        absolute_url = relative_url
    return JsonResponse({'url': absolute_url})

