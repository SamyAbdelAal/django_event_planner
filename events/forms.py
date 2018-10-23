from django import forms
from django.contrib.auth.models import User
from .models import *

class UserSignup(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email' ,'password']

		widgets={
		'password': forms.PasswordInput(),
		}


class UserLogin(forms.Form):
	username = forms.CharField(required=True)
	password = forms.CharField(required=True, widget=forms.PasswordInput())


class EventForm(forms.ModelForm):
	class Meta:
		model = Event
		exclude = ['organizer']

		widgets = {
			'date':  forms.DateInput(attrs={'type':'date'}),
			'time':  forms.DateInput(attrs={'type':'time'}), 
		}

class BookingForm(forms.ModelForm):
	class Meta:
		model = BookedEvent
		fields = ['tickets']

class UpdateProfile(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']