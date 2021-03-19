from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment
from taggit.models import Tag
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)


# Create your views here.


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/list.html'

def post_list(request, tag_slug=None):
    object_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 2)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/list.html', {
        'page': page,
        'posts': posts,
        'tag': tag,
    }
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # List of active comments for this post
    # ! Uses 'related_name' in Comments model -> Post foreign key
    comments = post.comments.filter(active=True)

    submitted = False

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # Create comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Finally save post to the database
            new_comment.save()
            submitted = True

            comment_form = CommentForm()

            return redirect(post)
    else:
        comment_form = CommentForm()

        # List of similar posts
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                                      .exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                                     .order_by('-same_tags', '-publish')[:4]

        return render(request, 'blog/detail.html', {
            'post': post,
            'comments': comments,
            'submitted': submitted,
            'comment_form': comment_form,
            'similar_posts': similar_posts
        })


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data

            # Sending Email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} ({cd["email"]}) recommends you reading "{post.title}"'
            message = f'Read "{post.title}" at {post_url}\n\n{cd["name"]}\'s comments: {cd["comments"]}'
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        # request was 'GET', need to display empty form
        form = EmailPostForm()
    return render(request, 'blog/share.html', {
        'post': post,
        'form': form,
        'sent': sent
    })


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.published.annotate(
            #     search=SearchVector('title', 'body'),
            # ).filter(search=query)
            search_vector = SearchVector('title', weight='A') + \
                SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')

    return render(request, 'blog/search.html', {
        'form': form,
        'query': query,
        'results': results,
    })