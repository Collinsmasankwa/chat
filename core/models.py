from django.db import models
from django.contrib.auth import get_user_model
import uuid
from .serializers import UserSerializer


User = get_user_model()

# for testing purposes use kpassword1 as pass

# room 
class Room(models.Model):
    room_name = models.CharField(max_length=500)
    room_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                       blank=True, null=True, related_name='created_by')
    online_users = models.ManyToManyField(User)
    users_typing = models.ManyToManyField(User, related_name='users_typing')
    participants = models.ManyToManyField(User, related_name='participants')

    def add_participant(self, user):
        self.participants.add(user)
        self.save()

    def get_all_participants_details(self):
        participants = []
        for user in self.participants.all():
            user_object = User.objects.get(username=user.username)
            user_profile = Profile.objects.get(user=user_object)
            participants.append((UserSerializer(user_object).data['username'], user_profile.profile_image.url))
        return participants
    
    def get_all_participants_count(self):
        return self.participants.count()

    def add_typing_user(self, user):
        self.users_typing.add(user)
        self.save()

    def remove_typing_user(self, user):
        self.users_typing.remove(user)
        self.save()

    def get_all_users_typing(self):
        users_typing = []
        for user in self.users_typing.all():
            user_object = User.objects.get(username=user.username)
            users_typing.append(UserSerializer(user_object).data['username'])
        return users_typing

    def online_count(self):
        return self.online_users.count()
    
    def add_user(self, user):
        self.online_users.add(user)
        self.save()

    def remove_user(self, user):
        self.online_users.remove(user)
        self.save()

    def get_online_users_list(self):
        online_users = []
        for user in self.online_users.all():
            user_object = User.objects.get(username=user.username)
            user_profile = Profile.objects.get(user=user_object)
            online_users.append((UserSerializer(user_object).data['username'], user_profile.profile_image.url))
        return online_users

    def __str__ (self):
        return f'{self.room_name} Room'
           

# message model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    message_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__ (self):
        return f'{self.sender} sent a message to {self.room} room'           
    

# user profile 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_profile = models.IntegerField()
    profile_image = models.ImageField(default='profile_images/user.png', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.username} profile'
    
