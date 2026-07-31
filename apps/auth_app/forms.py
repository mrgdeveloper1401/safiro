# apps/auth_app/forms.py
from django.contrib.auth.forms import SetUnusablePasswordMixin, BaseUserCreationForm


class AdminUserCreationForm(SetUnusablePasswordMixin, BaseUserCreationForm):

    usable_password = SetUnusablePasswordMixin.create_usable_password_field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
