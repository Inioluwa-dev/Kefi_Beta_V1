import json
from channels.generic.websocket import AsyncWebsocketConsumer


class DMConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f'WebSocket connect: me={self.scope.get("user")}, url_route={self.scope.get("url_route")})')
        self.me = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs'].get('username')
        if not self.other_username:
            print('No username in url_route kwargs:', self.scope['url_route']['kwargs'])
            await self.close()
            return
        self.other_user = await self.get_user(self.other_username)
        if not self.me.is_authenticated or not self.other_user:
            await self.close()
            return
        self.room_name = self.get_room_name(self.me.username, self.other_username)
        self.room_group_name = f'dm_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')
        if event_type == 'message':
            message = data.get('message')
            await self.save_message(self.me, self.other_user, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.me.username,
                }
            )
        elif event_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'sender': self.me.username,
                }
            )
        elif event_type == 'not_typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'not_typing',
                    'sender': self.me.username,
                }
            )
        elif event_type == 'read':
            await self.mark_messages_read(self.me, self.other_user)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read',
                    'sender': self.me.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender'],
        }))

    async def not_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'not_typing',
            'sender': event['sender'],
        }))

    async def read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'sender': event['sender'],
        }))

    @staticmethod
    def get_room_name(user1, user2):
        return '_'.join(sorted([user1, user2]))

    @staticmethod
    async def get_user(username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return await User.objects.aget(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    async def save_message(sender, recipient, content):
        from .models import Message
        await Message.objects.acreate(sender=sender, recipient=recipient, content=content, is_read=False)

    @staticmethod
    async def mark_messages_read(reader, other_user):
        from .models import Message
        await Message.objects.filter(sender=other_user, recipient=reader, is_read=False).aupdate(is_read=True) 