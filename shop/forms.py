from django import forms

from shop.models import ProductReview

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int, widget=forms.Select(attrs={'class': 'form-select mb-3'}))
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ('rating', 'comment')
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "type": "range",
                    "class": "form-range",
                    "min": "1",
                    "max": "5",
                    "step": "1",
                }
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,"maxlength":2000,"placeholder": "Write a review"}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['rating'].initial = 3

