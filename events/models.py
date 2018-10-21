from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.core.validators import MaxValueValidator , MinValueValidator
class Event(models.Model):
	organizer = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
	title = models.CharField(max_length=120)
	description = models.TextField()
	date= models.DateField( null=True,blank=True )
	seats = models.IntegerField(null=True,blank= True)
	def __str__(self):
		return self.title

	def get_seats_remaining(self):
		#booked = BookedEvent.objects.get(event__id=self.id)
		# if BookedEvent.objects.filter(event__id=self.id).exists() :
		# 	booked =  BookedEvent.objects.get(event__id=self.id)
		# 	print(booked)
		# 	self.seats = self.seats - booked.tickets
		# 	print(booked.tickets) 
		return self.seats

	@property
	def is_past_due(self):
	    return date.today() > self.date
class BookedEvent(models.Model):
	event= models.ForeignKey(Event, default=1, on_delete=models.CASCADE)
	user = models.ForeignKey(User,  default=1, on_delete=models.CASCADE)
	tickets = models.IntegerField(null=True,blank= True)

	def check_seats(self):
		return (self.tickets <= self.event.seats)
		
	def get_seats(self):
		return self.event.seats
	
	def __str__(self):
		return "Event:%s User:%s" % (self.event.title, self.user.username)