from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
import markdown

from .models import Post
from .forms import CommentForm


def post_list(request, tag_slug=None):
    tag = None
    if tag_slug:
        tag = Tag.objects.filter(slug=tag_slug).first()
        all_posts = Post.objects.filter(tags__in=[tag])
    else:
        all_posts = Post.objects.all()
    tag_list = Tag.objects.all()
    paginator = Paginator(all_posts, 4)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'tag_list': tag_list,
        'tag_slug': tag_slug,
        'tag': tag,
    }

    return render(request, 'posts/list.html', context)


def post_detail(request, year, month, day, slug):
    posts = Post.objects.filter(
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=slug
    ).first()

    markdown_extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.md_in_html',
        'markdown.extensions.tables',
        'markdown.extensions.admonition',
        'markdown.extensions.codehilite',
        'markdown.extensions.legacy_attrs',
        'markdown.extensions.legacy_em',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks',
    ]

    posts.body = markdown.markdown(posts.body, extensions=markdown_extensions)

    comments = posts.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = posts
            new_comment.save()
            return redirect('posts:post_detail', year=year, month=month, day=day, slug=slug)
    else:
        comment_form = CommentForm()
    tag_list = Tag.objects.all()

    context = {
        'posts': posts,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'tag_list': tag_list,
    }

    return render(request, 'posts/detail.html', context)
