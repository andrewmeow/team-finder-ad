from django import forms
from .models import Project
from users.forms import clean_github


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Название проекта'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Опишите суть проекта, цели, технологии...'
            }),
            'github_url': forms.URLInput(attrs={
                'placeholder': 'https://github.com/username/repo'
            }),
            'status': forms.Select(),
        }

    def clean_github_url(self):
        return clean_github(self)
