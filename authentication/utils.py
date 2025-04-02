from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str

class AppTokenGenerator(PasswordResetTokenGenerator):
    def __make_hash_value(self, user, timestamp):
        return (force_str(user.is_active)+force_str(user.pk)+force_str(timestamp))
    
token_generator = AppTokenGenerator()