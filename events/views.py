from django.shortcuts import render, redirect
from django.contrib.auth import (
	authenticate,
	login,
	logout,
	update_session_auth_hash
	  )
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from .forms import *
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from .models import *
from datetime import datetime,timedelta
import pytz
import time


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
	if request.user.is_anonymous:
		return redirect('login')

	events = Event.objects.filter(organizer=request.user)
	query = request.GET.get('q')
	if query:
		events = events.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(ogranizer__username__icontains=query)
		).distinct()

	# attended_list = request.user.bookedevent_set.all().values_list('event', flat=True)
	# attnded = Event.objects.filter(id__in=attended_list) # simplfiy
	attendedevent_list = request.user.bookedevent_set.filter(event__date__lte=timezone.now(), event__time__lte=timezone.now().today().time())
	#booked_list = request.user.bookedevent_set.filter(event__date__gte=timezone.now(),event__time__gt=timezone.now().time())
	booked_list = request.user.bookedevent_set.filter(Q(event__date=timezone.now().date(),event__time__gt=timezone.now().today().time())|Q(event__date__gt=timezone.now().date())).distinct()
	context = {
	   "events": events,
	   "attendedevent_list": attendedevent_list, 
	   "booked_list":booked_list,
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
	if request.method == "POST":
		tickets = int(request.POST.get("tickets"))
		if event.seats >= int(tickets):
			event.seats =int(event.seats-tickets)
			event.save()
			BookedEvent.objects.create(event=event,user=request.user,tickets=tickets)# pass three parameters
			messages.success(request, "Successfully Booked!")
			return redirect('event-detail', event_id=event.id)
		else:
			messages.info(request, "You exceeded the limit")

	context = {
		"event":event,
	}
	return render(request, 'event_booked.html', context)


def event_list(request):
	print("timezone.now.time:", timezone.now().today().time())
	#events = Event.objects.filter( date__gte=timezone.now().date())
	#print("Event time:", (events[0].time))
	print(timezone.now())
	events = Event.objects.filter(Q(date=timezone.now().date(),time__gt=timezone.now().today().time())|Q(date__gt=timezone.now().date())).distinct()
	booked_list = BookedEvent.objects.filter(event=events)
	query = request.GET.get('q')
	if query:
		events = events.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(organizer__username__icontains=query)
		).distinct()

	context = {
	   "events": events,
	   "booked_list":booked_list,
	}
	return render(request, 'event_list.html', context)

def profile_edit(request):
	if not (request.user.is_staff or not request.user.is_anonymous):
		return redirect ('signin')
	form = UpdateProfile(instance=request.user)
	profile_form = ProfileForm(instance=request.user.profile)
	if request.method == "POST":
		form = UpdateProfile(request.POST, request.FILES , instance=request.user)
		profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if form.is_valid() and profile_form.is_valid:	
			form.save()
			profile_form.save()
			# profile= form.save(commit=False)
			# profile.first_name = request.POST.get("first_name")
			# profile.last_name = request.POST.get("last_name")
			# profile.email = request.POST.get("email")
			# profile.set_password(request.POST.get("password"))
			# profile.save()
			messages.success(request, "Successfully Edited!")
			return redirect('dashboard-list')
		print (form.errors)
	context = {
	"form": form,
	"profile_form":profile_form,
	}
	return render(request, 'profile_edit.html', context)

def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('dashboard-list')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	context = {
		'form': form
	}
	return render(request, 'change_passowrd.html', context)

def profile_detail(request, user_id):
	user_profile = Profile.objects.get(user__id=user_id)
	user = User.objects.get(id=user_id)
	events = Event.objects.filter(organizer=user)
	today = datetime.today() 
	thirty_days_ago = today - timedelta(days=30) 
	forloopcounter = [0,1,2]
	attendedevent_list= user.bookedevent_set.filter(event__date__range=(thirty_days_ago, today)).order_by('-event__date')[0:3]
	# attendedevent_list = user.bookedevent_set.filter(event__date__lte=timezone.now(), event__time__lte=timezone.now())
	context = {
		"user_profile":user_profile,
		"attendedevent_list":attendedevent_list,
		"forloopcounter":forloopcounter,
		"events":events,
	}
	return render(request, 'profile.html', context)

def profile_ex(request):
	return render(request, 'profile_ex.html')



def cancel_event(request,booked_id,event_id):
	KW=pytz.timezone('Asia/Kuwait')
	bookedevent = BookedEvent.objects.get(id=booked_id)
	event = Event.objects.get(id=event_id)
	actual_time = timezone.localtime(timezone.now())
	date_time = datetime.combine(event.date, event.time).replace(tzinfo=KW)
	can_cancel= date_time - actual_time
	print(can_cancel)
	print (days_hours_minutes(can_cancel))
	# can_cancel = (can_cancel + datetime.hour + can_cancel).time()
	print(can_cancel)
	three_hours = (3,0)
	print (three_hours)
	if days_hours_minutes(can_cancel) >= three_hours :
		event.seats = event.seats + bookedevent.tickets
		event.save()
		bookedevent.delete()
		messages.success(request, 'Your booking was successfully canceled!')
		return redirect("dashboard-list")	
	else:
		messages.success(request, 'You can\'t cancel a booking 3 hours before an event!')
		return redirect("dashboard-list")	


def days_hours_minutes(td):
    return td.seconds//3600, (td.seconds//60)%60


def follow(request,user_id):
	if request.user.is_anonymous:
		return redirect('login')
	follower = Follower.objects.all()
	current_user = User.objects.get(id=request.user.id)
	followed_user = User.objects.get(id=user_id)
	#current_user.following.create(Follower(followed=followed_user))
	Follower.objects.create(follower=request.user, followed=followed_user)
	#current_user.following.save()
	messages.success(request,"Followed!")
	print(current_user.followers.all())
	return redirect('profile-detail', user_id)
