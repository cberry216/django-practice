from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.


def post_list(request):                               # Request required for all views
    posts = Post.published(all)                       # Get all published posts
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})                   # Context variables to be used within the page


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,                    # Return object or launches HTML 404 exception
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
