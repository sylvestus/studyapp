
from multiprocessing import context
from unicodedata import name

from django.shortcuts import render,redirect
from .models import Message, Room,Topic,User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.db.models import Q
# from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse

# Create your views here.
def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ""
  # Q is used to filter with more than one parameters
  rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )
    
  # topc__name queries the topic name of the topic in rooms as a foreighn key
  # icontains is case insensitive contains
  topics = Topic.objects.all()[0:6]
  # limits the querry set to 6 items the rest can be viewed by clicking more
  room_count = rooms.count()
  room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
  return render(request,'base/index.html',{'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages})

@login_required(login_url='login')
def room(request, pk):
 
  room= Room.objects.get(id=pk)
  room_messages=room.message_set.all() 
  # message is the model name in lowercase to user the set.all()   querries the child  objects of a specific room
  # gives the sets of messages related to this specific room ,,,one to many
  participants = room.participants.all()

  if request.method == 'POST':
    message = Message.objects.create(
        user = request.user,
        room = room,
        body = request.POST.get('body')
    )
    # create method creates the message
    room.participants.add(request.user)
    # adds user to participants once they comment
    return redirect('room',pk = room.id)
    # ensures the page fully refreshes incase the user decides to make another post request

  context = {'room':room, 'room_messages':room_messages, 'participants':participants}

  return render(request,'base/room.html',context)

@login_required(login_url='login')
def userProfile(request,pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all()
  topics = Topic.objects.all()
  room_messages=user.message_set.all() 
  context = {'user':user, 'rooms':rooms, 'topics':topics,'room_messages':room_messages}
  return render(request, 'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name = topic_name)
    # if thevalue is new it will create but if it alreay exists it will get
    Room.objects.create(
      host = request.user,
      topic =  topic,
      name = request.POST.get('name'),
      description = request.POST.get('description')
    )

    # form = RoomForm(request.POST)
    # if form.is_valid():
    #   room = form.save(commit=False)
    #   room.host = request.user
    #   room.save()
    return redirect('home')
  context = {'form':form,'topics':topics}
  return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
  # use the create room form to update
  room= Room.objects.get(id=pk)
  # instance makes the form prefilled with the data the room instance currently holds
  form = RoomForm(instance=room) 
  topics = Topic.objects.all()

  if request.user != room.host:
    return HttpResponse('you are not allowed here!!')
    # prevents people in the room from deleting rooms created by a different host,,, you can only delete your own work

  if request.method =='POST':
    form = RoomForm(request.POST, instance=room) 
    # instance = Room tells it which room to update
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name = topic_name)
    # if thevalue is new it will create but if it alreay exists it will get 
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()
    return redirect('home')
  
  context = {'form':form,'topics':topics,'room':room}
  return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.user != room.host:
    return HttpResponse('you are not allowed here!!')
    # prevents people in the room from deleting rooms created by a different host,,, you can only delete your own work

  if request.method == 'POST':
    room.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj':room})

def loginPage(request):
  page = 'login'
  if request.user.is_authenticated:
    # prevents user from re-loging in  
    return redirect('home')
  if request.method == 'POST':
    email = request.POST.get('email').lower()
    password = request.POST.get('password')

    try:
      user = User.objects.get(email=email)
    except:
        messages.error(request, "user doesn't exist")
    user = authenticate(request, email=email, password=password)
    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, "Username OR Password doesn't exist")
  context={'page':page}
  return render(request, 'base/login_register.html', context)

def logoutUser(request):
  logout(request)
  return redirect('home')

def registerPage(request):
  page='register'
  form = MyUserCreationForm()
  if request.method == 'POST':
    form = MyUserCreationForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.username = user.username.lower()
        user.save()
        login(request, user)
        # logs in the registered user
        return redirect('home')
    else:
      messages.error(request, 'registration error')
  context={'page':page, 'form':form}
  return render(request, 'base/login_register.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if request.user != message.user:
    return HttpResponse('you are not allowed here!!')
    # prevents people in the room from deleting rooms created by a different host,,, you can only delete your own work

  if request.method == 'POST':
    message.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
  user =request.user
  form = UserForm(instance=user)
  if request.method == 'POST':
    form = UserForm(request.POST,request.FILES, instance=user)
    if form.is_valid():
      form.save()
    return redirect('user-profile',pk=user.id)

  return render(request,'base/update-user.html',{'form':form})


@login_required(login_url='login')
def topicsPage(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ""
  topics=Topic.objects.filter(name__icontains=q)
  return render(request,'base/topics.html',{'topics':topics})

@login_required(login_url='login')
def activityPage(request):
  room_messages = Message.objects.all()
  return render(request,'base/activity.html',{'room_messages':room_messages})