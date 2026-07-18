from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountVerificationTokenGenerator(PasswordResetTokenGenerator):
    pass


account_verification_token = AccountVerificationTokenGenerator()
