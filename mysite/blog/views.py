from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/list.html'

# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 2)
#     page = request.GET.get('page')

#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range, deliver last page of results
#         posts = paginator.page(paginator.num_pages)

#     return render(
#         request,
#         'blog/list.html',
#         {'page': page, 'posts': posts}
#     )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    post_params = [
        post.publish.year,
        post.publish.month,
        post.publish.day,
        post.slug
    ]

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

            return redirect(post, {
                'post': post,
                'comments': comments,
                'submitted': submitted,
                'comment_form': comment_form
            })
    else:
        comment_form = CommentForm()
        return render(request, 'blog/detail.html', {
            'post': post,
            'comments': comments,
            'submitted': submitted,
            'comment_form': comment_form
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
