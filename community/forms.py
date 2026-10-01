from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter your title",
                    "class": "form-control",
                },
            ),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Enter your content",
                    "rows": "4",
                    "cols": "40",
                    "class": "form-control",
                },
            ),
        }
