from django import forms

from shop.models import ProductReview, Order

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES,
        coerce=int,
        widget=forms.Select(attrs={"class": "form-select mb-3"}),
    )
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.RadioSelect(
                attrs={
                    "class": "review-rating__slider",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "maxlength": 2000,
                    "placeholder": "Write a review",
                },
            ),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "full_name",
            "email",
            "phone_number",
            "shipping_method",
            "country",
            "eircode",
            "town_or_city",
            "street_address1",
            "street_address2",
            "county",
        )

    def __init__(self, *args, **kwargs):

        placeholders = {
            "full_name": "Full name",
            "email": "Email address",
            "phone_number": "Phone number",
            "country": "Country",
            "eircode": "Eircode",
            "town_or_city": "town or city",
            "street_address1": "Street address",
            "street_address2": "Street address (optional)",
            "county": "County",
        }

        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != "shipping_method":
                self.fields[field].widget.attrs.update(
                    {
                        "class": "form-control my-2",
                        "placeholder": placeholders[field],
                    }
                )
            else:
                self.fields["shipping_method"].widget.attrs.update(
                    {
                        "class": "form-select my-2",
                        "placeholder": "Select shipping method",
                    }
                )
