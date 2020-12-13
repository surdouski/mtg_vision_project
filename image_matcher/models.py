from django.db import models


class ImageUpload(models.Model):
    image_input = models.ImageField(upload_to='uploads/')
    image_name = models.CharField(max_length=80, null=True, blank=True)

    def delete(self, *args, **kwargs):
        try:
            self.image_input.delete()
        except Exception:
            pass  # if file doesn't exist that's ok
        super().delete(*args, **kwargs)
