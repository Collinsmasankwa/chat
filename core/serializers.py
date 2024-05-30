###### don't add another serializer here, we'll get into circular import errors #########

from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
