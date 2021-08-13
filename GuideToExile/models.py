from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from djongo import models


class SkillGem(models.Model):
    is_enabled = models.BooleanField()
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True


class SkillGroup(models.Model):
    is_enabled = models.BooleanField()
    main_active_skill_index = models.IntegerField()
    gems = models.ArrayField(
        model_container=SkillGem
    )

    class Meta:
        abstract = True


class TreeSpec(models.Model):
    title = models.CharField(max_length=255)
    nodes = models.JSONField()
    url = models.CharField(max_length=1000)
    tree_version = models.CharField(max_length=255)

    class Meta:
        abstract = True


class ItemSet(models.Model):
    set_id = models.IntegerField()
    title = models.CharField(max_length=255)
    slots = models.JSONField()

    class Meta:
        abstract = True


class Item(models.Model):
    item_id_in_itemset = models.IntegerField()
    name = models.CharField(max_length=255)
    base_name = models.CharField(max_length=255)
    rarity = models.CharField(max_length=255)
    display_html = models.CharField(max_length=5000)

    class Meta:
        abstract = True


class Keystone(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=255)


class UniqueItem(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=255)


class PobDetails(models.Model):
    build_stats = models.JSONField()
    class_name = models.CharField(max_length=255)
    ascendancy_name = models.CharField(max_length=255)
    skill_groups = models.ArrayField(
        model_container=SkillGroup
    )
    main_active_skills = models.JSONField()
    tree_specs = models.ArrayField(
        model_container=TreeSpec
    )
    active_tree_spec_index = models.IntegerField()
    items = models.ArrayField(
        model_container=Item
    )

    item_sets = models.ArrayField(
        model_container=ItemSet
    )
    active_item_set_index = models.IntegerField()

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=150)
    bio = models.TextField()
    signup_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class BuildGuide(models.Model):
    build_id = models.ObjectIdField()
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    pob_string = models.CharField(max_length=40000)
    pob_details = models.EmbeddedField(model_container=PobDetails)
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=40000)
    unique_items = models.ManyToManyField(UniqueItem, related_name='unique_items_related_builds')
    keystones = models.ManyToManyField(Keystone, related_name='keystones_related_builds')


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
