from django.db import models


class TutorManager(models.Manager):

    def create_default_tutor_with_user(self, user):

        # change to enabled=False after rep testing!!!

        tutor = self.model(
            user=user,
            enabled=True,
            num_seshes=0,
            ave_rating_1=5,
            ave_rating_2=5,
            ave_rating_3=5,
            credits=0,
            did_accept_terms=False,
            bonus_points=0
        )
        tutor.save()
        return tutor
