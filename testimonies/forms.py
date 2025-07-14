from django import forms
from modeltranslation.forms import TranslationModelForm
from .models import Testimony

class TestimonyForm(TranslationModelForm):
    class Meta:
        model = Testimony
        fields = ['comment', 'rating']  # Isso agora incluirá comment_en, comment_pt etc.
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
