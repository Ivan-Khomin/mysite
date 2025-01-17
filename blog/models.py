from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from taggit.managers import TaggableManager
from slugify import slugify


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
    tags = TaggableManager(verbose_name='Теги')

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'

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

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Post, self).save(*args, **kwargs)


def save_images(instance, filename):
    post_id = instance.post_id
    return 'gallery_images/{}/{}'.format(post_id, filename)


class PostPoint(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        default=None,
        verbose_name='Пост етапу готування'
    )
    post_point_text = models.TextField(verbose_name='Текст етапу готування')
    post_image = models.ImageField(
        upload_to=save_images,
        blank=True,
        verbose_name='Зображення пункту'
    )
    post_header = models.CharField(
        max_length=250,
        default='HEADER',
        verbose_name='Шапка етапу готування'
    )

    class Meta:
        verbose_name = 'Етап готування'
        verbose_name_plural = 'Етапи готування'

    def __str__(self):
        return 'Пункт поста {}'.format(self.post.title)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост коментаря'
    )
    name = models.CharField(max_length=80, verbose_name='Ім\'я')
    email = models.EmailField()
    body = models.TextField(verbose_name='Текст коментаря')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    active = models.BooleanField(default=True, verbose_name='Статус')

    class Meta:
        ordering = ['created']
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

    def __str__(self):
        return 'Коментар написаний {} о {}'.format(self.name, self.post)
