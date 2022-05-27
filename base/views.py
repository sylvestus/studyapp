from django.shortcuts import render

# Create your views here.

rooms = [
    {'id':1, 'name':'lets learn python'},
     {'id':2, 'name':'Design with me'},
      {'id':3, 'name':'Frontend developer'},
]
def home(request):
  message='home'
  return render(request,'base/index.html',{'rooms':rooms})

def room(request):
  message='room'
  return render(request,'base/room.html',{'message':message})