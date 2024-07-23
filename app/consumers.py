from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import sync_to_async
import json
from .models import *
from django.contrib.auth.models import User



class UpdateRealtime(AsyncConsumer):
    async def websocket_connect(self,event):
        print("websocket connected...",event)
        print("## Channel Layer...", self.channel_layer)    # get default channel layer from a project
        print("## Channel Name...", self.channel_name)    # get channel Name
        print(self.scope['url_route']['kwargs']['groupname'])  # scope is similar to request in views
        print("Group Name ....",self.scope['url_route']['kwargs']['groupname']) # extracting groupname from url
        
        user=self.scope['user'].id
        self.group_name = self.scope['url_route']['kwargs']['groupname']
        self.id = self.scope['url_route']['kwargs']['hall']  # see routing.py url 
        print(self.group_name)
        print(user)
        await self.channel_layer.group_add(self.group_name,self.channel_name)  # Creating group name group_add('<group_name>',self.channel_name)

        await self.send({
            'type':'websocket.accept',
            })
     

    async def websocket_receive(self,event):
        print("message received from client...",event)
        print("Type of Message Received form Client...",type(event['text']))  # checking type 
        #  need to convert string into python type as we need to save chat msg
        data = json.loads(event['text'])
        seat = data['seat']
        action = data['action']
        print('accessing Actual data',seat) 
        print('accessing Actual data',action) 
        
        # Authenticate USER if FAIL DON"T SAVE OR SEND MSG 
        if self.scope['user'].is_authenticated:
            message = {
            'type': 'seat_status',
            'seat': seat,
            'status': 'selected' if action == 'select' else 'deselected',
            }
            # Save selected seat
            user = await sync_to_async(User.objects.get)(id=self.scope['user'].id)
            movie = await sync_to_async(Movie.objects.get)(movie_name=self.group_name)
            screening = await sync_to_async(Screening.objects.get)(movie=movie)
            seatclass = await sync_to_async(Seat_Class.objects.get)(name='Gold')
            seatinstance = await sync_to_async(Seat.objects.get)(seat_number=seat,seat_class=seatclass)

            try:
                if action == 'select':
                    await sync_to_async(SeatSelect.objects.get_or_create)(seat = seatinstance, screening = screening, user = user)
                elif action == 'deselect':
                    await sync_to_async(SeatSelect.objects.filter)(seat = seatinstance, screening = screening, user = user).delete()
            except:
                pass

                
            # Broadcasting seat selection to all clients in the group
            await self.channel_layer.group_send(self.group_name, {
                'type': 'seat_status',
                'message': json.dumps(message)
            })
        else:
            await self.send({
                'type': 'websocket.send',
                'text': json.dumps({'msg': 'Login Required', 'user': 'unknown'})
            })


    async def seat_status(self, event):
        print("# Event...", event)
        
        # Send message to WebSocket
        await self.send({
            'type': 'websocket.send',
            'text':event['message']
        })
    
    async def seat_clear(self,event):
        await self.send({
            'type': 'websocket.send',
            'text':event['message']
        })


    async def seat_updated(self,event):
        await self.send({
            'type': 'websocket.send',
            'text':event['message']
        })

    async def websocket_disconnect(self,event):
        print("websocket disconnected...",event)
        print("## Channel Layer...", self.channel_layer)  
        print("## Channel Name...", self.channel_name)

        # Group Discard code
        await self.channel_layer.group_discard(self.group_name,self.channel_name)
        raise StopConsumer
    

