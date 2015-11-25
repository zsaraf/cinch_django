from django.db import models


class StudentManager(models.Manager):

    def create_default_student_with_user(self, user):
        student = self.model(
            user=user,
            credits=0
        )
        student.save()
        return student
