from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition border-gray-300",
                "placeholder": "••••••••",
            }
        )
    )

    class Meta:
        model = User
        fields = ["phone", "first_name", "last_name", "password"]
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition border-gray-300",
                    "placeholder": "+998901234567",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition border-gray-300",
                    "placeholder": "Ismingiz",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition border-gray-300",
                    "placeholder": "Familiyangiz",
                }
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
