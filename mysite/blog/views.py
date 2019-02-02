from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post

# Create your views here.


def post_list(request):                               # Request required for all views
    object_list = Post.published.all()
    paginator = Paginator(object_list, 1)             # Only 1 post per page
    page = request.GET.get('page')                    # Current page (integer)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:                          # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:                                 # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts})                   # Context variables to be used within the page


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
