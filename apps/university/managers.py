from django.db import models


class SchoolManager(models.Manager):

    def get_school_from_email(self, email):
        '''
        Finds the school from an email
        '''
        domain = email.split('@')[1]
        split_domain = domain.split('.')
        host = ""
        if len(split_domain) > 1:
            host = split_domain[len(split_domain) - 2]
        host += "." + split_domain[len(split_domain) - 1]
        try:
            school = self.model.objects.get(email_domain=host)
            return school

        except self.model.DoesNotExist:

            # look through special domains
            return None
