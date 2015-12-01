from django.db import models
from django.utils.crypto import get_random_string


class TokenManager(models.Manager):

    def generate_new_token(self):
        '''
        Finds a new unique access token
        '''
        while True:
            unique_string = get_random_string(length=32)

            if self.model.objects.filter(session_id=unique_string).count() == 0:
                token = self.model(
                    session_id=unique_string
                )
                token.save()
                return token


class DeviceManager(models.Manager):

    def update_device_token(self, user, device_token, device_type, device_model, system_version, app_version, timezone_name):
        '''
        Updates the device token for the user
        '''
        # Clear out any device tokens not associated with the user
        if device_token:
            self.model.objects.filter(token=device_token).exclude(user=user).delete()

        # Clear out any other rows with the user with different tokens
        self.model.objects.filter(user=user).exclude(token=device_token).delete()

        try:
            device = self.model.objects.get(user=user)
            device.token = device_token
            device.type = device_type
            device.device_model = device_model
            device.system_version = system_version
            device.app_version = app_version
            device.timezone_name = timezone_name

        except self.model.DoesNotExist:
            device = self.model(
                user=user,
                token=device_token,
                type=device_type,
                device_model=device_model,
                system_version=system_version,
                app_version=app_version,
                timezone_name=timezone_name,
            )

        device.save()
