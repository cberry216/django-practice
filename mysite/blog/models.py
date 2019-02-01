from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.


class PublishedManager(models.Manager):                   # Custom model manager to get posts that are 'published'
    def get_queryset(self):
        return super(PublishedManager, self)\
            .get_queryset()\
            .filter(status='published')                   # Same query, but filtered only on 'published'


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    objects = models.Manager()                             # Default manager
    published = PublishedManager()                        # Custom manager for the Post model

    title = models.CharField(max_length=250)              # === VARCHAR()
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')    # Can't have same slug AND publish value
    author = models.ForeignKey(User,                      # Defines a many-to-one relationship
                               on_delete=models.CASCADE,  # If the user is deleted, all blog posts are deleted
                               related_name='blog_posts')  # Allows a backwards relationship (less code to write)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)  # Default value when created
    created = models.DateTimeField(auto_now_add=True)     # Sets the value to 'now' when object is CREATED
    updated = models.DateTimeField(auto_now=True)         # Sets the value to 'now' when object is UPDATED
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')

    class Meta:                                           # Metadata about the class
        ordering = ('-publish',)                          # How to order the results (by results in descending order)

    def get_absolute_url(self):
        return reverse("blog:post_detail",                # Allows constructing URLs by their name and optional parameters
                       args=[
                           self.publish.year,
                           self.publish.month,
                           self.publish.day,
                           self.slug
                       ])

    def __str__(self):                                    # Human-readable format of object, used by admin site
        return self.title
