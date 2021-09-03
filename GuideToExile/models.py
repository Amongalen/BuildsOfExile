from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from GuideToExile import json_encoder


class Keystone(models.Model):
    name = models.CharField(max_length=255)


class UniqueItem(models.Model):
    name = models.CharField(max_length=255)


class UserProfileManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(user__username=username)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    name = models.CharField(max_length=60)
    base_class_name = models.CharField(max_length=60)


class BuildGuide(models.Model):
    guide_id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=255)
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    creation_datetime = models.DateTimeField(blank=True, null=True)
    modification_datetime = models.DateTimeField(blank=True, null=True)
    pob_string = models.CharField(max_length=40000)
    pob_details = models.JSONField(encoder=json_encoder.BuildDetailsJsonEncoder,
                                   decoder=json_encoder.BuildDetailsJsonDecoder)
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=40000)
    unique_items = models.ManyToManyField(UniqueItem, related_name='unique_items_related_builds')
    keystones = models.ManyToManyField(Keystone, related_name='keystones_related_builds')
    ascendancy_class = models.ForeignKey(AscendancyClass, on_delete=models.SET_NULL, null=True)


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


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


@receiver(pre_save, sender=BuildGuide)
def build_guide_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
