from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from GuideToExile import json_encoder, settings


class Keystone(models.Model):
    name = models.CharField(max_length=255)


class UniqueItem(models.Model):
    name = models.CharField(max_length=255)


class ActiveSkill(models.Model):
    name = models.CharField(max_length=255)


class UserProfileManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(user__username=username)


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractUser):
    objects = CustomUserManager()


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    twitch_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    signup_confirmation = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    timezone = models.TextField(blank=True, null=True)
    liked_guides = models.ManyToManyField('BuildGuide', through='GuideLike')

    objects = UserProfileManager()

    def natural_key(self):
        return self.user.username

    def __str__(self):
        return self.user.username


class AscendancyClass(models.Model):
    class BaseClassName(models.IntegerChoices):
        MARAUDER = 1, 'Marauder'
        RANGER = 2, 'Ranger'
        WITCH = 3, 'Witch'
        DUELIST = 4, 'Duelist'
        TEMPLAR = 5, 'Templar'
        SHADOW = 6, 'Shadow'
        SCION = 7, 'Scion'

    class AscClassName(models.IntegerChoices):
        JUGGERNAUT = 1, 'Juggernaut'
        BERSERKER = 2, 'Berserker'
        CHIEFTAIN = 3, 'Chieftain'
        DEADEYE = 4, 'Deadeye'
        RAIDER = 5, 'Raider'
        PATHFINDER = 6, 'Pathfinder'
        NECROMANCER = 7, 'Necromancer'
        ELEMENTALIST = 8, 'Elementalist'
        OCCULTIST = 9, 'Occultist'
        SLAYER = 10, 'Slayer'
        GLADIATOR = 11, 'Gladiator'
        CHAMPION = 12, 'Champion'
        INQUISITOR = 13, 'Inquisitor'
        HIEROPHANT = 14, 'Hierophant'
        GUARDIAN = 15, 'Guardian'
        ASSASSIN = 16, 'Assassin'
        SABOTEUR = 17, 'Saboteur'
        TRICKSTER = 18, 'Trickster'
        ASCENDANT = 19, 'Ascendant'
        NONE = 20, 'None'

    name = models.PositiveSmallIntegerField(choices=AscClassName.choices)
    base_class_name = models.PositiveSmallIntegerField(choices=BaseClassName.choices)
    asc_name_v2l_mapping = {i.value: i.label for i in AscClassName}
    base_name_v2l_mapping = {i.value: i.label for i in BaseClassName}
    asc_name_l2v_mapping = {i.label: i.value for i in AscClassName}
    base_name_l2v_mapping = {i.label: i.value for i in BaseClassName}

    @property
    def icon_name(self):
        if self.name == AscendancyClass.AscClassName.NONE:
            icon_name = self.base_name_v2l_mapping[self.base_class_name]
        else:
            icon_name = self.asc_name_v2l_mapping[self.name]
        return icon_name

    @property
    def portrait_icon(self):
        return f'/icons/{self.icon_name.lower()}.png'

    @property
    def portrait_icon_80x80(self):
        return f'/icons/{self.icon_name.lower()}_80x80.png'

    def __str__(self):
        if self.name == AscendancyClass.AscClassName.NONE:
            name = self.base_name_v2l_mapping[self.base_class_name]
        else:
            name = self.asc_name_v2l_mapping[self.name]
        return name


class BuildGuide(models.Model):
    class GuideStatus(models.IntegerChoices):
        DRAFT = 1, 'draft'
        PUBLIC = 2, 'public'
        ARCHIVED = 3, 'archived'

    guide_id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=180)
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    creation_datetime = models.DateTimeField(blank=True, null=True)
    modification_datetime = models.DateTimeField(blank=True, null=True)
    pob_string = models.CharField(max_length=40000, null=True)
    pob_details = models.JSONField(encoder=json_encoder.BuildDetailsJsonEncoder,
                                   decoder=json_encoder.BuildDetailsJsonDecoder, null=True)
    title = models.CharField(max_length=180, null=True)
    text = models.CharField(max_length=40000, null=True)
    unique_items = models.ManyToManyField(UniqueItem, related_name='unique_items_related_builds')
    keystones = models.ManyToManyField(Keystone, related_name='keystones_related_builds')
    primary_skills = models.ManyToManyField(ActiveSkill)
    ascendancy_class = models.ForeignKey(AscendancyClass, on_delete=models.SET_NULL, null=True)
    draft = models.OneToOneField('BuildGuide', on_delete=models.CASCADE, related_name='public_version', null=True)
    status = models.PositiveSmallIntegerField(choices=GuideStatus.choices)

    @property
    def is_draft(self):
        return self.status == BuildGuide.GuideStatus.DRAFT

    @property
    def is_public(self):
        return self.status == BuildGuide.GuideStatus.PUBLIC

    @property
    def is_archived(self):
        return self.status == BuildGuide.GuideStatus.ARCHIVED


class GuideLike(models.Model):
    guide = models.ForeignKey(BuildGuide, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_relation', fields=['guide', 'user'])
        ]


class GuideComment(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    guide = models.ForeignKey(BuildGuide, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    creation_datetime = models.DateTimeField()
    modification_datetime = models.DateTimeField()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


@receiver(pre_save, sender=BuildGuide)
def build_guide_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
