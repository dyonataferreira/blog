from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import Http404

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import re

def extract_thumbnail(content):
    """Extrai URL da primeira imagem do conteúdo HTML"""
    if not content:
        return None
    img_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', flags=re.IGNORECASE)
    media_re = re.compile(r'(?:https?:)?//[^/]+(/media/[^"\'\s>]+)|(/media/[^"\'\s>]+)')
    
    m = img_re.search(content)
    if m:
        return m.group(1)
    
    m2 = media_re.search(content)
    if m2:
        return m2.group(1) or m2.group(2)
    
    return None

def get_posts_with_preview(posts):
    """Retorna posts com thumbnails extraídos"""
    posts_with_preview = []
    for p in posts:
        preview = extract_thumbnail(p.content)
        posts_with_preview.append({'post': p, 'thumb': preview})
    return posts_with_preview

# LISTAR
def post_list(request):
    sort = request.GET.get('sort', '-created_at')
    
    # Validar tipo de ordenação
    if sort not in ['-created_at', 'created_at']:
        sort = '-created_at'
    
    posts = Post.objects.all().order_by(sort)
    posts_with_preview = get_posts_with_preview(posts)
    
    # Obter categorias que têm posts
    from django.db.models import Count
    categories = Category.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gte=1).order_by('name')
    
    return render(request, 'posts/post_list.html', {
        'posts_with_preview': posts_with_preview,
        'categories': categories,
        'sort': sort
    })

# LISTAR POR CATEGORIA
def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    sort = request.GET.get('sort', '-created_at')
    
    # Validar tipo de ordenação
    if sort not in ['-created_at', 'created_at']:
        sort = '-created_at'
    
    posts = category.posts.all().order_by(sort)
    posts_with_preview = get_posts_with_preview(posts)
    
    # Obter categorias que têm posts
    from django.db.models import Count
    categories = Category.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gte=1).order_by('name')
    
    return render(request, 'posts/post_list.html', {
        'posts_with_preview': posts_with_preview,
        'categories': categories,
        'current_category': category,
        'sort': sort
    })

# DETALHE
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        raise Http404("Post não encontrado")
    
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

