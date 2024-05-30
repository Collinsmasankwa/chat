"""
URL configuration for chatproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:username>/<str:room_name>/', views.room, name='room'),
    path('create_or_get_room/<str:username>/<str:room_name>/', views.create_room, name='create_or_get_room'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('get_user_created_rooms/', views.get_user_created_rooms, name='get_user_created_rooms'),
    path('get_user_joined_rooms/', views.get_user_joined_rooms, name='get_user_joined_rooms'),
]
