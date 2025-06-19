from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'}),
        }

    def __init__(self, *args, **kwargs):
        hide_recipient = kwargs.pop('hide_recipient', False)
        super().__init__(*args, **kwargs)
        if hide_recipient:
            self.fields.pop('recipient')