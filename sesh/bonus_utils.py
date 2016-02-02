from apps.university.models import BonusPointAllocation
from apps.account.models import PastBonus
from apps.tutor.models import TutorTier
from mandrill_utils import EmailManager
from rest_framework import exceptions
import locale
locale.setlocale(locale.LC_ALL, '')


class BonusManager:

    END_SESH = "sesh_completed_points"
    END_DIRECT_SESH = "direct_sesh_completed_points"
    REFER_USER = "user_referral_points"
    REFER_TUTOR = "tutor_referral_points"
    MONTHLY_GOAL = "monthly_point_goal"

    BONUS_FILENAME = "monthly_bonus_description.txt"

    @staticmethod
    def award_points_for_action(user, action):
        # get school row or default, if no row for school_id
        bonus_allocation = BonusPointAllocation.objects.filter(school_id__in=[0, user.school.pk]).order_by('-school_id')[0]
        new_points = getattr(bonus_allocation, action) + user.tutor.bonus_points
        goal_points = getattr(bonus_allocation, BonusManager.MONTHLY_GOAL)

        if (new_points >= goal_points):
            new_points = new_points - goal_points
            user.tutor.credits += bonus_allocation.bonus_amount
            PastBonus.objects.create(user=user, amount=bonus_allocation.bonus_amount, is_tier_bonus=False)
            merge_vars = {
                "MONTHLY_BONUS_AMOUNT": locale.currency(bonus_allocation.bonus_amount)
            }
            EmailManager.send_email(EmailManager.TUTOR_RECEIVED_BONUS, merge_vars, user.email, user.readable_name, None)

        user.tutor.bonus_points = new_points
        user.tutor.save()

    @staticmethod
    def check_tier_status(user):
        try:
            tier = TutorTier.objects.get(sesh_prereq=user.tutor.num_seshes)
            user.tutor.credits += tier.bonus_amount
            user.tutor.save()
            PastBonus.objects.create(user=user, amount=tier.bonus_amount, is_tier_bonus=True)
            merge_vars = {
                'FIRST_NAME': user.first_name,
                'NUM_SESHES': user.tutor.num_seshes,
                'NEXT_TIER': tier.name,
                'REWARD_AMOUNT': '${}'.format(tier.bonus_amount),
                'IMG_SRC': tier.image_url
            }

            EmailManager.send_email(EmailManager.TUTOR_REACHED_NEXT_LEVEL, merge_vars, user.email, user.readable_name, None)

        except TutorTier.DoesNotExist:
            # didn't earn a new tier
            pass
