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
from django.core.mail import send_mail
from django.conf import settings


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
	attendedevent_list = request.user.bookedevent_set.filter(event__date__lte=timezone.now(), event__time__lte=timezone.now().today().time())
	booked_list = request.user.bookedevent_set.filter(Q(event__date=timezone.now().date(),event__time__gt=timezone.now().today().time())|Q(event__date__gt=timezone.now().date())).distinct()

	if query:
		events = events.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(organizer__username__icontains=query)
		).distinct()
		attendedevent_list = attendedevent_list.filter(
			Q(event__title__icontains=query)|
			Q(event__description__icontains=query)|
			Q(event__organizer__username__icontains=query)
		).distinct()
		booked_list = booked_list.filter(
			Q(event__title__icontains=query)|
			Q(event__description__icontains=query)|
			Q(event__organizer__username__icontains=query)
		).distinct()
	context = {
	   "events": events,
	   "attendedevent_list": attendedevent_list, 
	   "booked_list":booked_list,
	}
	return render(request, 'dashboard.html', context)

def event_create(request):
	if request.user.is_anonymous:
		return redirect('login')
	following_usernames =Follower.objects.filter(followed = request.user) #get followers to send mass emails
	form = EventForm()
	if request.method == "POST":
		form = EventForm(request.POST, request.FILES)
		if form.is_valid():
			event = form.save(commit=False)
			event.organizer = request.user
			event.save()
			for followed_user in following_usernames:
				send_mail(
				    '%s has created a new event!'% request.user.username,
				    '%s has made a new event \n Event information: \n Title: %s \n Description: %s \n Date: %s \n Time: %s \n ' %(request.user.username, event.title,event.description,event.date,event.time) ,
				    'from@example.com',
				    [followed_user.follower.email],
				)
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
	if request.user.is_anonymous:
		return redirect('signin')
	event = Event.objects.get(id=event_id)
	if request.method == "POST":
		tickets = int(request.POST.get("tickets"))
		if event.seats >= int(tickets):
			event.seats =int(event.seats-tickets)
			event.save()
			bk = BookedEvent.objects.create(event=event,user=request.user,tickets=tickets)# pass three parameters
			send_mail(
					    '%s booking information'% (bk.event.title),
					    'You successfully booked %s ticket(s) for %s \n \
					    Event information: \n Title: %s \n Description: %s \n Date: %s \n Time: %s \n ' 
					    %(tickets,bk.event.title, bk.event.title,bk.event.description,bk.event.date,bk.event.time) ,
					    '',
					    ['sam.omran@hotmail.com'],
					    fail_silently=False,
				)
			messages.success(request, "Successfully Booked, you should recieve an email!")
			return redirect('event-detail', event_id=event.id)
		else:
			messages.info(request, "You exceeded the limit")

	context = {
		"event":event,
	}
	return render(request, 'event_booked.html', context)


def profile_edit(request):
	if  not request.user.is_staff or request.user.is_anonymous:
		return redirect ('signin')
	form = UpdateProfileForm(instance=request.user)
	profile_form = ProfileForm(instance=request.user.profile)
	if request.method == "POST":
		form = UpdateProfileForm(request.POST, request.FILES , instance=request.user)
		profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if form.is_valid() and profile_form.is_valid:	
			form.save()
			profile_form.save()
			messages.success(request, "Successfully edited your profile!")
			return redirect('dashboard-list')
		print (form.errors)
	context = {
	"form": form,
	"profile_form":profile_form,
	}
	return render(request, 'profile_edit.html', context)

def change_password(request):
	if request.user.is_anonymous or not request.user.is_staff:
		return redirect("signin")
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
	attendedevent_list= user.bookedevent_set.filter(event__date__range=(thirty_days_ago, today)).order_by('-event__date')[0:3]
	following_users =Follower.objects.filter(follower = user).count()
	followed_users = Follower.objects.filter(followed = user).count()
	likes_by_users = LikedUser.objects.filter(liked = user).count()
	following_usernames =Follower.objects.filter(followed = user)[0:3]
	followed_usernames =Follower.objects.filter(follower = user)
	context = {
		"user_profile":user_profile,
		"attendedevent_list":attendedevent_list,
		"events":events,
		"following_users":following_users,
		"followed_users":followed_users,
		"likes_by_users":likes_by_users,
		"following_usernames":following_usernames,
		"followed_usernames":followed_usernames,

	}
	return render(request, 'profile.html', context)


def cancel_event(request,booked_id,event_id):
	KW=pytz.timezone('Asia/Kuwait')
	bookedevent = BookedEvent.objects.get(id=booked_id)
	event = Event.objects.get(id=event_id)
	actual_time = timezone.now().today()
	date_time = datetime.combine(event.date, event.time)
	can_cancel= date_time - actual_time
	three_hours = (0,3,0)
	if days_hours_minutes(can_cancel) >= three_hours :
		event.seats = event.seats + bookedevent.tickets
		event.save()
		send_mail(
			    '%s canceled from %s'% (request.user.username, bookedevent.event.title),
			    '%s has canceled %s ticket(s) for %s ' %(request.user.username,bookedevent.tickets,bookedevent.event.title) ,
			    '',
			    ['sam.omran@hotmail.com'],
			    fail_silently=False,
				)
		bookedevent.delete()
		messages.success(request, 'Your booking was successfully canceled!')
		return redirect("dashboard-list")	
	else:
		messages.success(request, 'You can\'t cancel a booking 3 hours before an event!')
		return redirect("dashboard-list")	


def days_hours_minutes(td):
	return td.days,td.seconds//3600, (td.seconds//60)%60


def follow(request,user_id):
	if request.user.is_anonymous:
		return redirect('login')
	if request.user.id==user_id:
		return redirect('profile-detail', user_id)
		messages.info(request,"You can't follow yoursrlf, silly!")
	followed_user = User.objects.get(id=user_id)
	f_user , created = Follower.objects.get_or_create(follower= request.user, followed=followed_user)
	f_Objs = Follower.objects.filter(followed= followed_user).count() 
	if created:
		action= "followed"
	else:
		action="unfollowed"
		f_user.delete()
		f_Objs = Follower.objects.filter(followed= followed_user).count()
	data = {
	"action": action,
	"f_Objs":f_Objs,
	"followed_user": followed_user.username,
	}
	return JsonResponse(data, safe=False)


def like(request,user_id):
	if request.user.is_anonymous:
		return redirect('login')
	liked_user = User.objects.get(id=user_id)
	l_user , created = LikedUser.objects.get_or_create(liker= request.user, liked=liked_user)
	l_Objs = LikedUser.objects.filter(liked= liked_user).count() 
	if created:
		action= "liked"
	else:
		action="unliked"
		l_user.delete()
		l_Objs = LikedUser.objects.filter(liked= liked_user).count()
	data = {
	"action": action,
	"l_Objs":l_Objs,
	"liked_user":liked_user.username,
	}
	return JsonResponse(data, safe=False)

def ev_li(request):
	events = Event.objects.filter(Q(date=timezone.now().today().date(),time__gt=timezone.now().today().time())|Q(date__gt=timezone.now().date())).distinct()
	booked_list = BookedEvent.objects.filter(event=events)
	user = User.objects.all()
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
	return render(request, 'events.html', context)



