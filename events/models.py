from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.dispatch import receiver

class Event(models.Model):
	organizer = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
	title = models.CharField(max_length=120)
	description = models.TextField()
	date= models.DateField( null=True,blank=True )
	time=models.TimeField( null=True, blank=True)
	seats = models.IntegerField(null=True,blank= True)
	def __str__(self):
		return "ID:%s Event:%s " % (self.id, self.title)

class BookedEvent(models.Model):
	event= models.ForeignKey(Event, default=1, on_delete=models.CASCADE)
	user = models.ForeignKey(User,  default=1, on_delete=models.CASCADE)
	tickets = models.IntegerField(null=True,blank= True)

	def check_seats(self):
		return (self.tickets <= self.event.seats)
		
	def get_seats(self):
		return self.event.seats
	
	def __str__(self):
		return "ID:%s Event:%s User:%s" % (self.id, self.event.title, self.user.username)


class Profile(models.Model):
	user = models.OneToOneField(User, default=1, on_delete=models.CASCADE)
	location = CountryField()
	bio = models.TextField(max_length=300, blank=True)
	birth_date = models.DateField(null=True, blank=True)
	profile_pic = models.ImageField(default="/profile_pic/pic placeholder.png/",upload_to='profile_pic', null=True, blank=True)

	def __str__(self):
		return "ID:%s User:%s " % (self.id, self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Follower(models.Model):
	follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
	followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
   
	class Meta:
		unique_together = ('follower', 'followed')

	def __str__(self):
		return '%s follows %s' % (self.follower.username, self.followed.username)

class LikedUser(models.Model):
	liker = models.ForeignKey(User, related_name='liking' , on_delete=models.CASCADE)
	liked = models.ForeignKey(User, related_name='likee' , on_delete=models.CASCADE)

	class Meta:
		unique_together = ('liker', 'liked')

	def __str__(self):
		return '%s likes %s' % (self.liker.username, self.liked.username)