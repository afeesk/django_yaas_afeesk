from django import forms
from django.contrib.auth import get_user_model
from auctionApp.models import Auction
from .models import UserProfile

User = get_user_model()

class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget = forms.PasswordInput())

	def clean_username(self):
		username = self.cleaned_data.get("username")
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			raise forms.ValidationError("Are you sure you are regitered? We cannot find this user.")
		return username

	def clean_password(self):
		username = self.cleaned_data.get("username")
		password = self.cleaned_data.get("password")
		try:
			user = User.objects.get(username=username)
		except:
			user = None
			#raise forms.ValidationError("Are you sure you are regitered? We cannot find this user.")
		if user is not None and not user.check_password(password): #user exist and password incorrect
			raise forms.ValidationError("Invalid password")
		elif user is None:
			pass
		else:
			return password

class RegistrationForm(forms.ModelForm):
	email  = forms.EmailField(label = 'Your Email')
	password1 = forms.CharField(label = 'Password', widget= forms.PasswordInput())
	password2 = forms.CharField(label = 'Password Confirmation', widget= forms.PasswordInput())

	class Meta:
		model = User
		fields = ['username', 'email']
		#fields = ['username']

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2 and password1 !=password2:
			raise forms.ValidationError("Password do not match")
		return password2

	def clean_email(self):
		email = self.cleaned_data.get("email")
		#user_count = User.objects.filter(email=email).count()
		email_count = User.objects.filter(email=email).count()
		if email_count >0:
			raise forms.ValidationError("This email has already been registered. Please use a different email")
		return email


	def save(self, commit = True):
		user = super(RegistrationForm, self).save(commit = False)
		user.set_password(self.cleaned_data['password1'])
		#user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class ModifyForm(forms.ModelForm):
	email  = forms.EmailField(label = 'Your Email')
	password1 = forms.CharField(label = 'Password', widget= forms.PasswordInput())
	class Meta:
		model = User
		fields = ['email']

	def clean_email(self):
		email = self.cleaned_data.get("email")
		#user_count = User.objects.filter(email=email).count()
		email_count = User.objects.filter(email=email).count()
		if email_count >0:
			raise forms.ValidationError("This email has already been registered. Please use a different email")
		return email

	def save(self, commit = True):
		user = super(ModifyForm, self).save(commit = False)
		user.set_password(self.cleaned_data['password1'])
		#user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class UserProfileForm(forms.ModelForm):
	language_preference = forms.CharField(widget=forms.HiddenInput())
	class Meta:
		model = UserProfile
		fields = ['language_preference']
		#fields = ['username']

	def save(self, commit = True):
		profile = super(UserProfileForm, self).save(commit = False)
		if commit:
			profile.save()
		return profile