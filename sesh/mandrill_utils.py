import mandrill
mandrill_client = mandrill.Mandrill('EFEqF_IiFMOqUbNQUO_pbA')


class EmailManager:

    TRANSCRIPT_SUBMISSSION_RESPONSE_WITH_ACCOUNT = 'transcript-submission-response-with-account-v1'
    TRANSCRIPT_SUBMISSSION_RESPONSE_NO_ACCOUNT = 'transcript-submission-response-no-account-v1'
    TUTOR_APPROVAL_SUBMISSION = 'tutor-approval-submission'
    NEW_SESH_ACCOUNT = 'new-sesh-account-v1'
    YOUR_REFERRAL_HAD_THEIR_SESH = 'your-referral-had-their-sesh-v1'
    THANKS_FOR_SHARING_SESH = 'thanks-for-sharing-sesh'
    CASHOUT = 'cash-out-v1'
    REQUEST_TIMEOUT = 'request-timeout'
    FIRST_INSTANT_REQUEST_TIMEOUT = 'first-instant-request-timeout'
    FIRST_SCHEDULED_REQUEST_TIMEOUT = 'first-scheduled-request-timeout'
    CREDIT_ADDED_RECEIPT = 'credit-added-receipt-v1'
    CREDIT_RECEIVED = 'credit-received-v1'
    STUDENT_CANCELLED_SESH = 'student-cancels-on-tutor-promo-v1'
    TUTOR_CANCELLED_SESH = 'tutor-cancels-on-student-promo-v1'
    TUTOR_RECEIVED_BONUS = 'monthly-bonus-reached'
    TUTOR_REACHED_NEXT_LEVEL = 'tutor-reached-next-level'
    SEND_MORE_CREDITS = "send-more-credits"
    REVIEW_SESH_TUTOR = "review-sesh-tutor"
    TUTOR_FIRST_SESH_RECEIPT = 'tutor-first-sesh-receipt'
    REVIEW_SESH_STUDENT = "review-sesh-student"
    STUDENT_CANCELLATION_FEE_RECEIPT = 'student-cancellation-fee-receipt'
    TUTOR_CANCELLATION_FEE_RECEIPT = 'tutor-cancellation-fee-receipt'
    PAYMENT_FAILED = "payment-failed"

# NOTE: change in merge_vars format from php emailManager - now dict is just { MERGE_VAR_NAME:content, ... }
# example use:
#     recipient_email = "loetting@stanford.edu"
#     recipient_name = "Lilli"
#     attachments = None
#     template_name = 'become-a-tutor'

#     merge_vars = {'FIRST_NAME': 'Lilli'}

#     result = send_email(template_name, merge_vars, recipient_email, recipient_name, attachments)

    @staticmethod
    def send_email(template_name, merge_vars_dict, recipient_email, recipient_name, attachments, tag=None):
        try:
            message = {}
            message['to'] = [{
                'email': recipient_email,
                'name': recipient_name,
                'type': 'to'
            }]

            merge_vars = None
            if merge_vars_dict is not None:
                merge_vars = {}
                merge_vars['rcpt'] = recipient_email
                vars_arr = []
                for key in merge_vars_dict:
                    vars_arr.append({'name': key, 'content': merge_vars_dict[key]})
                merge_vars['vars'] = vars_arr
                message['merge_vars'] = [merge_vars]

            if attachments is not None:
                message['attachments'] = attachments

            if tag is not None:
                message['tags'] = [tag]

            async = False
            ip_pool = 'Main Pool'

            result = mandrill_client.messages.send_template(template_name=template_name, template_content=None, message=message, async=async, ip_pool=ip_pool, send_at=None)
            return result

        except mandrill.Error, e:
            # TO DO handle exception
            return 'A mandrill error occurred: %s - %s' % (e.__class__, e)
