from django.core.files.storage import FileSystemStorage
import os
from django.db import models


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
