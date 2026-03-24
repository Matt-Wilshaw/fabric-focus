from django.conf import settings
from datetime import datetime, timezone

from botocore.exceptions import ClientError
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

    def get_modified_time(self, name):
        """Return object modified time and tolerate missing-key race conditions.

        During collectstatic, django-storages can occasionally raise a HeadObject
        404 for keys that were listed moments earlier. Returning an old timestamp
        allows collectstatic to safely recopy the asset instead of failing the
        Heroku build.
        """
        try:
            return super().get_modified_time(name)
        except ClientError as exc:
            error_code = exc.response.get('Error', {}).get('Code')
            if error_code in {'404', 'NoSuchKey', 'NotFound'}:
                return datetime(1970, 1, 1, tzinfo=timezone.utc)
            raise


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION