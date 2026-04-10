from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_list(request):
    """View all conversations (for admin) or just the admin conversation (for user)"""
    if request.user.is_staff:
        # Get all users who have sent or received messages
        users_with_messages = User.objects.filter(
            Q(received_messages__sender=request.user) | 
            Q(sent_messages__recipient=request.user)
        ).distinct().exclude(id=request.user.id)
        
        return render(request, 'communications/chat_list.html', {
            'users': users_with_messages
        })
    else:
        return redirect('communications:user_chat')

@login_required
def admin_chat(request, user_id):
    """Chat interface for admin to talk to a specific user"""
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('home')
        
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            return redirect('communications:admin_chat', user_id=user_id)
            
    # Get conversation history
    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('created_at')
    
    # Mark incoming messages as read
    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'communications/chat.html', {
        'other_user': other_user,
        'chat_messages': chat_messages,
        'is_admin': True
    })

@login_required
def user_chat(request):
    """Chat interface for customer to talk to admin"""
    # Find an admin to talk to (first superuser found)
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        messages.error(request, "No administrator available to message right now.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=admin_user,
                content=content
            )
            return redirect('communications:user_chat')
            
    # Get conversation history
    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=admin_user)) |
        (Q(sender=admin_user) & Q(recipient=request.user))
    ).order_by('created_at')
    
    # Mark incoming messages as read
    Message.objects.filter(sender=admin_user, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'communications/chat.html', {
        'other_user': admin_user,
        'chat_messages': chat_messages,
        'is_admin': False
    })
