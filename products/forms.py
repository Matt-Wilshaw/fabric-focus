from django import forms
from django.core.exceptions import ValidationError
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):
    price = forms.DecimalField(
        label='Price (£)',
        min_value=0,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'min': 0,
            'step': '0.01',
        }),
        help_text='Enter pounds and pence, for example 12.99',
    )

    rating = forms.DecimalField(
        label='Rating (0.00 - 5.00)',
        required=False,
        min_value=0,
        max_value=5,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'min': 0,
            'max': 5,
            'step': '0.01',
        }),
    )

    class Meta:
        model = Product
        exclude = ('image_url',)

        image = forms.ImageField(label='Image', required=False,
                                 widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

    def clean_price(self):
        price = self.cleaned_data['price']
        raw_price = self.data.get('price', '')

        if ',' in raw_price:
            raise ValidationError('Use a decimal point as the separator, for example 12.99.')

        if '.' in raw_price:
            decimal_places = raw_price.split('.', 1)[1]
            if len(decimal_places) > 2:
                raise ValidationError('Use at most 2 decimal places, for example 12.99.')

        return price