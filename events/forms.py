from django import forms
from django.contrib.auth.models import User
from .models import Event,BookedEvent

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

		# widgets = {
		# 	'date':  forms.DateInput(attrs={'class':'datepicker'}),
 
		# }

class BookingForm(forms.ModelForm):
	class Meta:
		model = BookedEvent
		fields = ['tickets']

		# widgets = {
		# 	"tickets": forms.NumberInput(attrs={'max_value':get_seat_count()})
		# }
		# def get_seat_count(self):
		# 	return self.model.get_seats()