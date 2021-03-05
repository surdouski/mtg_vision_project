import logging
import pathlib
import urllib.parse

from requests import HTTPError
from django.db import models

from ebaysdk.trading import Connection as Trading
from django.core.files.storage import FileSystemStorage


from mtg_vision_project.settings import BASE_DIR, STATIC_URL, STATICFILES_DIRS, MEDIA_ROOT


def get_activated_api(user_refresh_token):
    from mtg_vision_project.ebay_oauth_python_client.oauthclient.oauth2api import \
        get_access_token
    file_path = BASE_DIR / pathlib.Path('ebay.yaml')
    try:
        """
        api = Trading(config_file=file_path, domain='api.sandbox.ebay.com',
                      token=user_access_token)
        return api
        """
        user_access_token = get_access_token(user_refresh_token)
        api = Trading(config_file=file_path, domain='api.sandbox.ebay.com',
                      token=user_access_token)
        return api
    except HTTPError as e:
        logging.exception(str(e))


def upload_image(api, image_upload_instance, user_refresh_token):
    """Uploads to ebay server for use in listing, returns url of hosted image."""

    try:
        path_to_image = _get_path_from_image_input(image_upload_instance)
        files = _get_ebay_image_file(path_to_image)
        picture_data = _get_picture_metadata(image_upload_instance)
        try:

            """
            print('why dont i have good error handling?')
            print(files)
            print(picture_data)
            print(api)
            print(path_to_image)
            """

            response = api.execute('UploadSiteHostedPictures', picture_data, files=files)
        except Exception as e:
            print('because im lazy')
            logging.exception(str(e))
            raise
        image_url = response.reply.get('SiteHostedPictureDetails').get('FullURL')
        image_upload_instance.update_url_details(image_url)
        return image_url
    except HTTPError as e:
        logging.exception(str(e))


def _get_picture_metadata(image_upload_instance):
    return {
        "WarningLevel": "Low",
        "PictureName": image_upload_instance.image_input.name,
    }


def _get_ebay_image_file(path_to_image):
    return {'file': ('EbayImage', open(path_to_image,
                                       'rb'))}


def _get_path_from_image_input(image_upload_instance):
    return STATICFILES_DIRS[0] + '/media/' + \
           image_upload_instance.image_input.name


class CardListingDetails(models.Model):
    scryfall_id = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    set = models.CharField(max_length=80)
    ebay_image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'name: {self.name}, set: {self.set}, url: {self.ebay_image_url}'


class OverwriteStorage(FileSystemStorage):
    """Used in ImageUpload for managing photos with the same name as a new image."""

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class ImageUpload(models.Model):
    image_input = models.ImageField(max_length=None, storage=OverwriteStorage(),
                                    upload_to='media/')
    image_name = models.CharField(max_length=80, null=True, blank=True)
    listing_details = models.ForeignKey(CardListingDetails, null=True,
                                        on_delete=models.PROTECT)

    def update_url_details(self, url):
        self.listing_details.ebay_image_url = url
        self.listing_details.save()
        return self.listing_details

    def delete(self, *args, **kwargs):
        try:
            self.image_input.delete()
        except Exception:
            pass  # if file doesn't exist that's ok
        super().delete(*args, **kwargs)
