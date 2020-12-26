from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class ImageUpload(models.Model):
    image_input = models.ImageField(max_length=None, storage=OverwriteStorage(),
                                    upload_to='uploads/')
    image_name = models.CharField(max_length=80, null=True, blank=True)

    def delete(self, *args, **kwargs):
        try:
            self.image_input.delete()
        except Exception:
            pass  # if file doesn't exist that's ok
        super().delete(*args, **kwargs)


class UserTokensProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_tokens_profile',
                                on_delete=models.PROTECT)
    access_token = models.CharField(max_length=2500, null=True, blank=True)
    refresh_token = models.CharField(max_length=150, null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_tokens_profile(sender, instance, created, **kwargs):
    if created:
        UserTokensProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_tokens_profile(sender, instance, created, **kwargs):
    instance.user_tokens_profile.save()
