from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count
# from django.views.generic import ListView

from taggit.models import Tag

from .models import Post, PostPoint, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 2) # По 2 статті на кожній сторінці.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Якщо сторінка не являється цілим числом, повертаємо першу сторінку.
        posts = paginator.page(1)
    except EmptyPage:
        # Якщо номер сторінки більше, ніж загальна кількість сторінок, повертаємо останню.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'page': page,
        'posts': posts,
        'tag': tag
    })


# class PostListView(ListView):
#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post_object = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    post_points = PostPoint.objects.filter(post=post_object)
    # Список активних коментарів для цієї статті.
    comments = post_object.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Користувач відправив коментар.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Створюємо коментар, але поки не зберігаємо в базі даних.
            cd = comment_form.cleaned_data
            new_comment = Comment(
                post=post_object,
                name=cd['name'],
                email=cd['email'],
                body=cd['comment']
            )
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post_object.tags.values_list('id', flat=True)
    # Формування списку схожих статтей.
    similar_posts = Post.objects.filter(tags__in=post_tags_ids, status='published').exclude(id=post_object.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', 'publish')[:4]

    return render(request, 'blog/post/detail.html', {
        'post': post_object,
        'post_points': post_points,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    })


def post_share(request, post_id):
    # Отримання статті по ідентифікатору
    post = get_object_or_404(Post, id=post_id, status='published')
    form = EmailPostForm()
    sent = False
    if request.method == 'POST':
        # Форма була відправлена на збереження.
        form = EmailPostForm()
        if form.is_valid():
            # Всі поля форми пройшли валідацію.
            cleaned_data = form.cleaned_data

            # Відправка електронною поштою.
            post_url = request.build_absolute_url(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(
                cleaned_data['name'],
                cleaned_data['email'],
                post.title
            )
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(
                post.title,
                post_url,
                cleaned_data['name'],
                cleaned_data['comment']
            )
            send_mail(subject, message, 'admin@myblog.com', [cleaned_data['to']])
            sent = True
        else:
            form = EmailPostForm()

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form
    })
