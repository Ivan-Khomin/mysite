from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
# from django.views.generic import ListView

from taggit.models import Tag

from .models import Post, PostPoint, Comment, User
from .forms import EmailPostForm, CommentForm, LoginForm, PostForm, PostPointForm, UserCreateForm, UserEditForm, SearchForm


@login_required
def post_list(request, tag_slug=None):
    search_form = SearchForm()
    query = None

    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            try:
                object_list = Post.objects.filter(title__contains=query, status='published')
            except:
                object_list = None
    else:
        object_list = Post.objects.filter(status='published')
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
        'tag': tag,
        'search_form': search_form
    })


# class PostListView(ListView):
#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 2
#     template_name = 'blog/post/list.html'


@login_required
def post_detail(request, year, month, day, post, post_id):
    post_object = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
        id=post_id
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
            cleaned_data = comment_form.cleaned_data
            new_comment = Comment(
                post=post_object,
                name=cleaned_data['name'],
                email=cleaned_data['email'],
                body=cleaned_data['comment']
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


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = authenticate(
                request,
                username=cleaned_data['username'],
                password=cleaned_data['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully!')
                else:
                    return HttpResponse('Disable account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'blog/account/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)

    return render(request, 'blog/registration/logged_out.html')


@login_required
def dashboard(request):
    user = request.user
    posts_pub = Post.objects.filter(author=user, status='published')
    posts_draft = Post.objects.filter(author=user, status='draft')

    return render(request, 'blog/account/dashboard.html', {
        'posts_pub': posts_pub,
        'posts_draft': posts_draft
    })


@login_required
def post_add(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            for tag in form.cleaned_data['tags']:
                post.tags.add(tag)
    else:
        form = PostForm()

    return render(request, 'blog/account/post_add.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_edit_form = PostForm(instance=post)
    if request.method == 'POST':
        post_edit_form = PostForm(request.POST, request.FILES, instance=post)
        if post_edit_form.is_valid():
            post_edit_form.save()

    return render(request, 'blog/account/post_edit.html', {
        'form': post_edit_form,
        'post': post
    })


@login_required
def post_delete(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return redirect('blog:dashboard')
    except Post.DoesNotExist:
        return redirect('blog:dashboard')


@login_required
def post_point_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_points = PostPoint.objects.filter(post=post)

    return render(request, 'blog/account/post_points.html', {
        'post': post,
        'post_points': post_points
    })


@login_required
def post_point_add(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostPointForm(request.POST, request.FILES)
        if form.is_valid():
            post_point = form.save(commit=False)
            post_point.post = post
            post_point.save()
    else:
        form = PostPointForm()

    return render(request, 'blog/account/post_point_add.html', {
        'form': form,
        'post': post
    })


@login_required
def post_point_edit(request, post_point_id):
    post_point = get_object_or_404(PostPoint, id=post_point_id)
    post = get_object_or_404(Post, id=post_point.post.id)

    if request.method == 'POST':
        post_point_edit_form = PostPointForm(request.POST, request.FILES, instance=post_point)
        if post_point_edit_form.is_valid():
            post_point_edit_form.save()
    else:
        post_point_edit_form = PostPointForm(instance=post_point)

    return render(request, 'blog/account/post_point_edit.html', {
        'form': post_point_edit_form,
        'post_point': post_point,
        'post': post
    })


@login_required
def post_point_delete(request, post_point_id):
    try:
        post_point = get_object_or_404(PostPoint, id=post_point_id)
        post_point.delete()
        return redirect('blog:post_point_list', post_id=post_point.post.id)
    except PostPoint.DoesNotExist:
        return redirect('blog:post_point_list')


def sign_up(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_user.save()
            login(
                request,
                authenticate(
                    username=user_form.cleaned_data['username'],
                    password=user_form.cleaned_data['password']
                )
            )
            return redirect('blog:post_list')
    else:
        user_form = UserCreateForm()

    return render(request, 'blog/registration/sign_up.html', {'user_form': user_form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, 'blog/account/profile.html', {'user_form': user_form})


def add_to_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.add(request.user)
    return redirect(
        'blog:post_detail',
        year=post.publish.year,
        month=post.publish.month,
        day=post.publish.day,
        post=post.slug,
        post_id=post.id
    )


def delete_from_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.remove(request.user)
    return redirect(
        'blog:post_detail',
        year=post.publish.year,
        month=post.publish.month,
        day=post.publish.day,
        post=post.slug,
        post_id=post.id
    )


def delete_from_favourite_in_dashboard(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.remove(request.user)
    return redirect('blog:favourite_posts')


def favourite_posts(request):
    return render(request, 'blog/account/fav_posts.html')
