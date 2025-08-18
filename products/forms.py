from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, PersonalizedCakeOrder


from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)



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

class PersonalizedCakeForm(forms.ModelForm):
    class Meta:
        model = PersonalizedCakeOrder
        fields = [
            "size", "flavor", "filling", "cover",
            "message", "topper_text", "roses_quantity",
            "reference_image", "quantity",
        ]
        widgets = {
            "message": forms.TextInput(attrs={"placeholder": "Mensagem no bolo"}),
            "topper_text": forms.TextInput(attrs={"placeholder": "Texto do topper (se houver)"}),
            "filling": forms.TextInput(attrs={"placeholder": "Ex.: brigadeiro, doce de leite..."}),
            "roses_quantity": forms.NumberInput(attrs={"min": 0}),
            "quantity": forms.NumberInput(attrs={"min": 1}),
        }