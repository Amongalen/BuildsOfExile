from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from GuideToExile import json_encoder


class Keystone(models.Model):
    name = models.CharField(max_length=255)


class UniqueItem(models.Model):
    name = models.CharField(max_length=255)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    twitch_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    signup_confirmation = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    timezone = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class BuildGuide(models.Model):
    build_id = models.BigAutoField(primary_key=True)
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


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


@receiver(pre_save, sender=BuildGuide)
def build_guide_pre_save_receiver(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
