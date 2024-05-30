from channels.generic.websocket import WebsocketConsumer
from .models import Room, Message,Profile
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import User


# chat consumer for messaging each other
class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.room = None
        self.user = None
        self.room_name  = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room = Room.objects.get(room_name=self.room_name)
        self.group_name = f'{self.room_name}-group'
        
        self.user = User.objects.get(username=self.username)

        # self.user = self.scope['user'] used with authentication

        self.accept()

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        # add user to list of online users
        self.room.add_user(self.user)

        # add user to list of participants
        self.room.add_participant(self.user)

        
        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'new_connection',
            'online_count': self.room.online_count(),
            'recent_user': self.user.username,
            'online_users_list': self.room.get_online_users_list(),
            'all_participants': self.room.get_all_participants_details(),
            'all_participants_count': self.room.get_all_participants_count(),
        })

        # get all messages for this room, if any and display
        all_messages = Message.objects.filter(room=self.room)
        self.broadcast_all_room_messages(all_messages, self.user.username)

    def broadcast_all_room_messages(self, messages_object, recent_user):
        for message in messages_object:
            async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'display_all_messages',
            'message': message.message,
            'sender': message.sender.username,
            'recent_user': recent_user,
            'sender_profile_image': Profile.objects.get(user=message.sender).profile_image.url,
            'time': str(message.created_at)[11:16]
        })     

    def display_all_messages(self, data):
        self.send(text_data=json.dumps(data))    

    def new_connection(self, data):
        self.send(text_data=json.dumps(data))    

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        self.room.remove_user(self.user)
        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'disconnection',
            'online_count': self.room.online_count(),
            'recent_user': self.user.username,
            'online_users_list': self.room.get_online_users_list(),
            'all_participants': self.room.get_all_participants_details(),
            'all_participants_count': self.room.get_all_participants_count(),
        })

    def disconnection(self, data):
        self.send(text_data=json.dumps(data))     

    def receive(self, text_data=None, bytes_data=None):
        parsed_message = json.loads(text_data)
        message = Message.objects.create(sender=self.user, message=parsed_message['message'], room=self.room)
        # broadcast the message to the group 
        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'broadcast_incoming_message',
            'message': parsed_message['message'],
            'sender': parsed_message['sender'],
            'sender_profile_image': Profile.objects.get(user=self.user).profile_image.url,
            'time': str(message.created_at)[11:16]
        })   

    def broadcast_incoming_message(self, data):
        self.send(text_data=json.dumps(data))    

    # handler for new typing connection, not used,
    # just to prevent this websocket from raising errors while MessageTyping consumer is used
    def new_typing_connection(self, data):
        self.send(text_data=json.dumps(data))  

    # handler for new typing connection, not used,
    # just to prevent this websocket from raising errors while MessageTyping consumer is used
    def no_typing_connection(self, data):
        self.send(text_data=json.dumps(data))      
    

# consumer for checking if a given user is typing or not on their keyboard
class MessageTypingConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.room = None
        self.user = None
        self.room_name  = None
        self.is_typing = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room = Room.objects.get(room_name=self.room_name)
        self.group_name = f'{self.room_name}-group'
        
        self.user = User.objects.get(username=self.username)

        # self.user = self.scope['user'] used with authentication

        self.accept()

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'new_typing_connection',
            'recent_user_typing': self.user.username,
            'users_typing_list': self.room.get_all_users_typing()
        })

    def new_typing_connection(self, data):
        self.send(text_data=json.dumps(data))     

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        self.room.remove_typing_user(self.user)
        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'no_typing_connection',
            'recent_user_typing': self.user.username,
            'users_typing_list': self.room.get_all_users_typing()
        })

    def no_typing_connection(self, data):
        self.send(text_data=json.dumps(data))    

    def receive(self, text_data=None, bytes_data=None):
        parsed_message = json.loads(text_data)
        self.is_typing = parsed_message['isTyping']
        
        if self.is_typing == 'True':
            # add user's typing to list of online users typing at the moment
            self.room.add_typing_user(self.user)
        else:
            self.room.remove_typing_user(self.user)
        
        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'new_typing_connection',
            'users_typing_list': self.room.get_all_users_typing()
        })

    # not used from chat consumer to avoid errors
    def new_connection(self, data):
        self.send(text_data=json.dumps(data))

    # not used from chat consumer to avoid errors
    def disconnection(self, data):
        self.send(text_data=json.dumps(data))

    # not used from chat consumer to avoid errors
    def broadcast_incoming_message(self, data):
        self.send(text_data=json.dumps(data))    

    # not used from chat consumer to avoid errors
    def display_all_messages(self, data):
        self.send(text_data=json.dumps(data))    
