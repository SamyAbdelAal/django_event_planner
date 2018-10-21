from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import *

def home(request):
	return render(request, 'home.html')

class Signup(View):
	form_class = UserSignup
	template_name = 'signup.html'

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			messages.success(request, "You have successfully signed up.")
			login(request, user)
			return redirect("home")
		messages.warning(request, form.errors)
		return redirect("signup")


class Login(View):
	form_class = UserLogin
	template_name = 'login.html'

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				messages.success(request, "Welcome Back!")
				return redirect('dashboard-list')
			messages.warning(request, "Wrong email/password combination. Please try again.")
			return redirect("login")
		messages.warning(request, form.errors)
		return redirect("login")


class Logout(View):
	def get(self, request, *args, **kwargs):
		logout(request)
		messages.success(request, "You have successfully logged out.")
		return redirect("login")

def dashboard(request):
	events = Event.objects.filter(organizer=request.user)
	query = request.GET.get('q')
	if query:
		events = events.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(ogranizer__username__icontains=query)
		).distinct()

	attended_list = request.user.bookedevent_set.all().values_list('event', flat=True)
	attnded = Event.objects.filter(id__in=attended_list)

	context = {
	   "events": events,
	   "attnded": attnded
	}
	return render(request, 'dashboard.html', context)

def event_create(request):
	if request.user.is_anonymous:
		return redirect('login')
	form = EventForm()
	if request.method == "POST":
		form = EventForm(request.POST, request.FILES)
		if form.is_valid():
			event = form.save(commit=False)
			event.organizer = request.user
			event.save()
			return redirect('dashboard-list')
	context = {
		"form":form,
	}
	return render(request, 'event_create.html', context)



def event_edit(request, event_id):
	event = Event.objects.get(id=event_id)
	if not (request.user.is_staff or request.user == event.organizer):
		return redirect ('signin')
	form = EventForm(instance=event)
	if request.method == "POST":
		form = EventForm(request.POST, instance=event)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('dashboard-list')
		print (form.errors)
	context = {
	"form": form,
	"event": event,
	}
	return render(request, 'event_edit.html', context)

def event_detail(request, event_id):
	event = Event.objects.get(id=event_id)
	attendees = BookedEvent.objects.filter(event=event)
	context = {
		"event": event,
		"attendees":attendees,
	}
	return render(request, 'event_detail.html', context)

def event_booked(request, event_id):
	event = Event.objects.get(id=event_id)
	form = BookingForm(instance=BookedEvent)
	if request.method == "POST":
		form = BookingForm(request.POST)
		if form.is_valid():
			bookedevent = form.save(commit=False)
			bookedevent.user = request.user
			bookedevent.event = event
			# if bookedevent.check_seats():
			if event.get_seats_remaining() >= bookedevent.tickets:
				event.seats =int(event.seats- bookedevent.tickets)
				event.save()
				bookedevent.save()
				messages.success(request, "Successfully Booked!")
				return redirect('event-detail', event_id=event.id)
			else:
				messages.info(request, "You exceeded the limit")

	context = {
		"form":form,
		"event":event,
	}
	return render(request, 'event_booked.html', context)


def event_list(request):
    events = Event.objects.all()
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(organizer__username__icontains=query)
        ).distinct()

    context = {
       "events": events,
    }
    return render(request, 'event_list.html', context)