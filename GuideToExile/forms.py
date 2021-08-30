import io
import logging

from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm

from GuideToExile import pob_import
from GuideToExile.models import UserProfile
from apps.django_tiptap.widgets import TipTapWidget

logger = logging.getLogger('guidetoexile')


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
            logger.error('Something went wrong while importing a build', exc_info=True)
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


class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('twitch_url', 'youtube_url', 'avatar')
        labels = {
            "avatar": "Profile image",
        }

    def clean_twitch_url(self):
        data = self.cleaned_data['twitch_url']
        if not data:
            return data
        data = data.lower()
        if (not data.startswith('https://twitch.tv')
            and not data.startswith('https://www.twitch.tv')
            and not data.startswith('http://twitch.tv')
            and not data.startswith('http://www.twitch.tv')):
            raise ValidationError('URL must start with "twitch.tv"')
        return data

    def clean_youtube_url(self):
        data = self.cleaned_data['youtube_url']
        if not data:
            return data
        data = data.lower()
        if (not data.startswith('https://youtube.com')
            and not data.startswith('https://www.youtube.com')
            and not data.startswith('http://youtube.com')
            and not data.startswith('http://www.youtube.com')):
            raise ValidationError('URL must start with "youtube.com"')
        return data

    def clean_avatar(self):
        data = self.cleaned_data['avatar']
        if data:
            im = data.read()
            image_file = io.BytesIO(im)
            image = Image.open(image_file)
            image = image.resize((200, 200), Image.ANTIALIAS)

            image_file = io.BytesIO()
            image.save(image_file, 'PNG', quality=90)

            data.file = image_file
        return data
