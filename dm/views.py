from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Message
from .forms import MessageForm
from django.db.models import Q

@login_required
def inbox_view(request):
    messages_qs = Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).order_by('-timestamp')
    # Show only the latest message per conversation
    conversations = {}
    for msg in messages_qs:
        other = msg.recipient if msg.sender == request.user else msg.sender
        if other not in conversations:
            conversations[other] = msg
    return render(request, 'dm/inbox.html', {'conversations': conversations.values()})

@login_required
def thread_view(request, username):
    other_user = get_object_or_404(User, username=username)
    thread_msgs = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=request.user))
    ).order_by('timestamp')
    # Mark messages as read
    thread_msgs.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.method == 'POST':
        form = MessageForm(request.POST, hide_recipient=True)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = other_user
            msg.save()
            messages.success(request, 'Message sent!')
            return redirect('dm:thread', username=other_user.username)
    else:
        form = MessageForm(hide_recipient=True)
    return render(request, 'dm/thread.html', {'thread_msgs': thread_msgs, 'form': form, 'other_user': other_user})

@login_required
def send_message_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            messages.success(request, 'Message sent!')
            return redirect('dm:thread', username=msg.recipient.username)
    else:
        form = MessageForm()
    return render(request, 'dm/send_message.html', {'form': form})
