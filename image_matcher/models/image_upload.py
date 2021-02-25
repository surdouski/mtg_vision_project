from django.db import models

from ebaysdk.trading import Connection as Trading
from django.core.files.storage import FileSystemStorage

from mtg_vision_project.settings import BASE_DIR


def get_activated_api(user_access_token):
    file_path = BASE_DIR / 'ebay.yaml'
    api = Trading(config_file=file_path, domain='api.sandbox.ebay.com',
                  token=user_access_token)
    return api


def upload_image(image_upload_instance, user_access_token):
    """Uploads to ebay server for use in listing, returns url of hosted image."""

    api = get_activated_api(user_access_token)
    files = {'file': ('EbayImage', open(image_upload_instance.image_input.url, 'rb'))}
    picture_data = {
        "WarningLevel": "Low",
        "PictureName": image_upload_instance.image_input.name,
    }
    response = api.execute('UploadSiteHostedPictures', picture_data, files=files)
    image_url = response.reply.get('SiteHostedPictureDetails').get('FullURL')
    return image_url


class OverwriteStorage(FileSystemStorage):
    """Used in ImageUpload for managing photos with the same name as a new image."""

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
