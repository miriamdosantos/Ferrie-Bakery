from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate category choices with only the 'name'
        categories = Category.objects.all()
        category_names = [(c.id, c.name) for c in categories]
        self.fields['category'].choices = category_names
        
        # Override required flags for the fields you want the user to fill in
        self.fields['category'].required = True
        self.fields['name'].required = True
        self.fields['price'].required = True
        self.fields['sale_option'].required = True

        # Apply a CSS class to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'border-black rounded-0'