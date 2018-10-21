from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Event(models.Model):
	organizer = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
	title = models.CharField(max_length=120)
	description = models.TextField()
	datetime = models.DateTimeField(default=timezone.now, )
	seats = models.IntegerField(null=True,blank= True)
	def __str__(self):
		return self.name


class BookedEvent(models.Model):
	event= models.ForeignKey(Event, default=1, on_delete=models.CASCADE)
	user = models.ForeignKey(User,  default=1, on_delete=models.CASCADE)