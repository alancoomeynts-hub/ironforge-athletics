from django import forms

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int, widget=forms.Select(attrs={'class': 'form-select mb-3'}))
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
