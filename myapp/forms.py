from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product


class CustomAdminUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'file']
        # exclude = ['seller', 'total_sale_amount', 'total_sale']
        labels = {
            "name": "Title"
        }
        error_messages = {
            'description': {
                'max_length': 'Keep the description under 300 letters',
                'min_length': 'Description must be al least 5 Characters long'
            },
            'file': {
                'required': 'Please, Select a file!'
            }
        }

    description = forms.CharField(
        max_length = 300,
        min_length = 5,
        widget = forms.Textarea
    )
    


# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(label='Password', min_length=4, max_length=20, widget=forms.PasswordInput, error_messages={
#         "min_length": "Password must be atleast 4 characters long",
#         "max_length": "Please, Enter a shorter Password"
#     })
#     confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email']
        
#         labels = {
#             "email": "Email",
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = self.cleaned_data['password']
#         confirm_password = self.cleaned_data['confirm_password']
#         if password != confirm_password:
#             raise forms.ValidationError('Password Do not match')

class UserRegistrationForm(UserCreationForm):

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Confirm passowrd'
        })
        
    )
    email = forms.CharField(
        required=True,
        error_messages= {
            'required': 'Must provide an unused email'
        },
        widget = forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }
        error_messages = {
            'username': {
                'required': 'Must provide an username'
            }
        }


class UserLoginForm(forms.Form):
    email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email address'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))