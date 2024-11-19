from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class Post(models.Model):
    STATUS_CHOICES = {
        ('draft', 'Draft'),
        ('published', 'Published')
    }

    title = models.CharField(max_length=250, verbose_name='Назва поста')
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_post',
        verbose_name='Автор'
    )
    short_description = models.CharField(max_length=250, verbose_name='Коротке описання')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Дата публікації')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата змінення')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус публікації'
    )
    image = models.ImageField(
        upload_to='product_images/',
        blank=False,
        verbose_name='Зображення'
    )
    tags = TaggableManager()

    class Meta:
        ordering = ['-publish']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )


def save_images(instance, filename):
    post_id = instance.post_id
    return 'gallery_images/{}/{}'.format(post_id, filename)


class PostPoint(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        default=None
    )
    post_point_text = models.TextField(verbose_name='Пункт поста')
    post_image = models.ImageField(
        upload_to=save_images,
        blank=True,
        verbose_name='Зображення пункту'
    )
    post_header = models.CharField(max_length=250, default='HEADER')

    def __str__(self):
        return 'Пункт поста {}'.format(self.post.title)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return 'Коментар написаний {} о {}'.format(self.name, self.post)
