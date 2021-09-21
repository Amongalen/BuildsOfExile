import io
import logging
from datetime import datetime, timedelta

from PIL import Image
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, Select

from GuideToExile import pob_import
from GuideToExile.models import UserProfile, AscendancyClass, ActiveSkill, Keystone, UniqueItem
from apps.django_tiptap.widgets import TipTapWidget

logger = logging.getLogger('guidetoexile')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2',)

    def clean_username(self):
        data = self.cleaned_data['username']
        if get_user_model().objects.filter(username__iexact=data).exists():
            raise ValidationError('Username already taken', code='username_taken')
        return data


class PobStringForm(Form):
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

    title = forms.CharField(max_length=180,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
                            help_text=None)
    primary_skills = forms.MultipleChoiceField(choices=(),
                                               widget=forms.SelectMultiple(attrs={'class': 'chosen-select'}),
                                               help_text=None)
    text = forms.CharField(max_length=40000, widget=TipTapWidget(attrs={'placeholder': 'Content'}), help_text=None)


class GuideListFilterForm(Form):
    base_class_name_choices = [(i.value, i.label) for i in AscendancyClass.BaseClassName]
    asc_class_name_choices = [(i.value, i.label) for i in AscendancyClass.AscClassName if i.label != 'None']
    base_class_name_choices.append((0, 'Any'))
    base_class_name_choices.sort()
    asc_class_name_choices.append((0, 'Any'))
    asc_class_name_choices.sort()

    title = forms.CharField(max_length=180, required=False, widget=forms.TextInput(attrs={'placeholder': 'Title...'}))
    base_class_name = forms.ChoiceField(required=True, choices=base_class_name_choices)
    asc_class_name = forms.ChoiceField(required=True, choices=asc_class_name_choices)
    author_username = forms.CharField(max_length=255, required=False, label='Author',
                                      widget=forms.TextInput(attrs={'placeholder': 'Author...'}))
    today = datetime.today()
    updated_after_offset = 90
    updated_after_initial = today - timedelta(days=updated_after_offset)
    updated_after = forms.DateField(
        initial=updated_after_initial.strftime("%Y-%m-%d"),
        localize=False,
        widget=forms.DateInput()
    )
    liked_by_me = forms.NullBooleanField(widget=Select(
        choices=[
            ('', 'Either'),
            (True, 'Yes'),
            (False, 'No'),
        ]
    ))

    active_skill = forms.ChoiceField(required=True, choices=())
    keystones = forms.MultipleChoiceField(required=False,
                                          choices=(),
                                          widget=forms.SelectMultiple(attrs={'class': 'chosen-select',
                                                                             'data-placeholder': 'Chooose Keystones...'}),
                                          help_text=None)

    unique_items = forms.MultipleChoiceField(required=False,
                                             choices=(),
                                             widget=forms.SelectMultiple(attrs={'class': 'chosen-select',
                                                                                'data-placeholder': 'Chooose Unique Items...'}),
                                             help_text=None)

    order_by = forms.ChoiceField(required=True,
                                 choices=[('Trending', 'Trending'),
                                          ('Popular', 'Popular'),
                                          ('Modification date', 'Modification date'),
                                          ('Creation date', 'Creation date'),
                                          ('Title', 'Title')],
                                 initial='Trending')

    def __init__(self, *args, **kwargs):
        super(GuideListFilterForm, self).__init__(*args, **kwargs)
        active_skill_choices = [(i + 1, skill.name) for i, skill in enumerate(
            ActiveSkill.objects.filter(buildguide__isnull=False).distinct().order_by(
                'name').all())]
        active_skill_choices.append((0, 'Any'))
        active_skill_choices.sort()
        self.fields['active_skill'].choices = active_skill_choices

        keystone_choices = [(i + 1, keystone.name) for i, keystone in
                            enumerate(Keystone.objects.filter(keystones_related_builds__isnull=False)
                                      .distinct().order_by('name').all())]
        self.fields['keystones'].choices = keystone_choices

        unique_item_choices = [(i + 1, keystone.name) for i, keystone in
                               enumerate(UniqueItem.objects.filter(unique_items_related_builds__isnull=False)
                                         .distinct().order_by('name').all())]
        self.fields['unique_items'].choices = unique_item_choices


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
