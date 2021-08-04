import traceback

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import Form

from BuildsOfExile import pob_import
from django_tiptap.widgets import TipTapWidget


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class NewGuideForm(Form):
    pob_input = forms.CharField(max_length=40000,
                                label="Enter Path of Building export code or a Pastebin link containing it")

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
    title = forms.CharField(max_length=255)
    text = forms.CharField(max_length=40000, widget=TipTapWidget())
