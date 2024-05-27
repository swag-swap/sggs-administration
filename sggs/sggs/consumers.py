import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.test_id = self.scope['url_route']['kwargs']['test_id']
        self.group_name = f'session_{self.session_id}_test_{self.test_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Notify teacher dashboard about the connection
        await self.channel_layer.group_send(
            f'teacher_dashboard_{self.session_id}_{self.test_id}',
            {
                'type': 'dashboard_message',
                'message': f'Student connected: {self.channel_name}'
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # Notify teacher dashboard about the disconnection
        await self.channel_layer.group_send(
            f'teacher_dashboard_{self.session_id}_{self.test_id}',
            {
                'type': 'dashboard_message',
                'message': f'Student disconnected: {self.channel_name}'
            }
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('activity')
            print(f"Received activity: {message}")

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'test_message',
                    'message': message
                }
            )

            # Forward the message to the teacher dashboard
            await self.channel_layer.group_send(
                f'teacher_dashboard_{self.session_id}_{self.test_id}',
                {
                    'type': 'dashboard_message',
                    'message': f'Student activity: {message}'
                }
            )
        except json.JSONDecodeError:
            print("Error decoding JSON")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def test_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

class TeacherDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.test_id = self.scope['url_route']['kwargs']['test_id']
        self.group_name = f'teacher_dashboard_{self.session_id}_{self.test_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            print(f"Received message on teacher dashboard: {message}")

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'dashboard_message',
                    'message': message
                }
            )
        except json.JSONDecodeError:
            print("Error decoding JSON")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def dashboard_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
