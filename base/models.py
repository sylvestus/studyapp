

from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User

class User(AbstractUser):
    name = models.CharField(max_length=200,null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True,default="avatar.svg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True) # if topic is deleted it wont delete the room but set its topic value to null
    name =models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null allows null values and blank alows for submission off a blank form field
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    # related namis used to give an alias to a model relation that had already been reffered to
    updated = models.DateTimeField(auto_now = True) # takes timestamp every time we save
    created = models.DateTimeField(auto_now_add= True) # takes timestamp once when an item was created

    class Meta:
        ordering = ['-updated', '-created'] # - ordering makes it order in a reversed order


    def __str__(self):
        return self.name
        
 
class Message(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now = True) # takes timestamp every time we save
    created = models.DateTimeField(auto_now_add= True) # takes timestamp once when an item was created

    class Meta:
        ordering = ['-updated', '-created'] # - ordering makes it order in a reversed order
         
    def __str__(self):
        return self.body[0:50] # to get the first 50 characters