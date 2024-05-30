from django.shortcuts import render
from .models import Room, Profile
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.core.serializers import serialize

# yah project mainne 31h 8 min se samapt chuka!


# homepage
@login_required(login_url='signin')
def index(request):
    msg = request.GET.get('msg', None)
    context = {
        'user': request.user,
        'msg': msg,
        'user': request.user.username
    }
    return render(request, 'index.html', context)


# create or get an existing room room
@login_required(login_url='signin')
def create_room(request, username, room_name):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({
            'response': 'User does not exist!'
        })
    else:
        if request.user.username == username:
            try:
                room = Room.objects.get(room_name=room_name)
            except Room.DoesNotExist:
                room = Room.objects.create(room_name=room_name, created_by=user)
                room.save()
                return JsonResponse({
                    'response': 'room created or got successfully'
                })
            else:
                return JsonResponse({
                    'response': 'room created or got successfully'
                })
        else:
            return JsonResponse({
                    'response': 'Oops, not your username!'
                })



# current room
@login_required(login_url='signin')
def room(request, username, room_name):
    room = Room.objects.get(room_name=room_name)
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user)
    context = {
        'user_profile': user_profile,
        'room': room
    }
    return render(request, 'room.html', context)
    

# signup 
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'response': 'Username already in use!'
                })
            else:
                if User.objects.filter(email=email).exists():
                    return JsonResponse({
                        'response': 'Email already in use'
                    })
                else:
                    # create user
                    new_user = User.objects.create_user(
                        username=username, email=email, password=password1
                    )
                    new_user.save()
                    # login user
                    user = auth.authenticate(username=username, password=password1)
                    auth.login(request, user)
                    # create new profile for this user
                    new_profile = Profile.objects.create(
                        user=user, id_profile=user.id
                    )
                    new_profile.save()
                    return JsonResponse({
                        'response': 'New Account created successfully!'
                    }, status=201)
        else:
            return JsonResponse({
                'response': 'Passwords do not match'
            })    

    return render(request, 'signup.html')


# signin 
def signin(request):
    msg = request.GET.get('msg', None)
    context = {
        'msg': msg,
    }

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return JsonResponse({
                'response': 'Logged in successfully'
            })
        else:
            return JsonResponse({
                'response': 'Invalid credentials'
            })
    return render(request, 'signin.html', context)


# logout
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return JsonResponse({
        'response': 'Logged out successfully'
    })

# get user's created rooms
@login_required(login_url='signin')
def get_user_created_rooms(request):
    created_rooms = Room.objects.filter(created_by=request.user)
    return JsonResponse({
        'response': json.loads(serialize('json', created_rooms))
    })


# get user's joined rooms, we didn't create the room
@login_required(login_url='signin')
def get_user_joined_rooms(request):
    joined_rooms = Room.objects.filter(participants=request.user).exclude(created_by=request.user)
    return JsonResponse({
        'response': json.loads(serialize('json', joined_rooms))
    })
