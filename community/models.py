from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import User



class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="posts")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=10,choices=Status.choices,default=Status.DRAFT,)

    class Meta:
        ordering = ("-created_on",)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField("image")
    caption = models.CharField(max_length=200, blank=True,)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Image for {self.post.title}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments",)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments",)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies",)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("created_on",)