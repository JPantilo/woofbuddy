from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('messages/', views.chat_list, name='chat_list'),
    path('chat/admin/<int:user_id>/', views.admin_chat, name='admin_chat'),
    path('chat/support/', views.user_chat, name='user_chat'),
]
