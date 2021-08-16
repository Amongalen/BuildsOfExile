import traceback

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import Form

from GuideToExile import pob_import
from apps.django_tiptap.widgets import TipTapWidget


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class NewGuideForm(Form):
    pob_input = forms.CharField(max_length=40000,
                                label="Enter Path of Building export code or a Pastebin link containing it",
                                widget=forms.TextInput(attrs={'class': ' form-control'}))

    def clean_pob_input(self):
        data = self.cleaned_data['pob_input']
        try:
            if data.startswith('https://pastebin.com'):
                data = pob_import.import_from_pastebin(data)

            xml = pob_import.base64_to_xml(data)
            return pob_import.parse_pob_details(xml), data
        except Exception as err:
            traceback.print_exc()
            raise ValidationError('Invalid export code or Pastebin link', code='invalid_pob_string')


class EditGuideForm(Form):
    def __init__(self, skill_choices, *args, **kwargs):
        super(EditGuideForm, self).__init__(*args, **kwargs)
        self.fields['primary_skills'].choices = skill_choices

    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}),
                            help_text=None)
    primary_skills = forms.MultipleChoiceField(choices=(),
                                               widget=forms.SelectMultiple(attrs={'class': 'chosen-select'}),
                                               help_text=None)
    text = forms.CharField(max_length=40000, widget=TipTapWidget(), help_text=None)
