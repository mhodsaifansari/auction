
import json
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import SyncConsumer
from asgiref.sync import async_to_sync
class ChatConsumer(WebsocketConsumer):
    def connect(self):
    
        self.room_group_name="listing-"+self.scope['url_route']['kwargs']['id']
        print(self.room_group_name)
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,self.channel_name)
        self.accept()
        
    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
        self.room_group_name,self.channel_name)
    # def receive(self,text_data):
    #     text_data_json=json.loads(text_data)
    #     bid=text_data_json["bid"]
        
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,{
    #             'type':'chat_message',
    #             'bid':bid
            
    #     })
    def chat_message(self,event):
        bid=event['bid']
        print(bid)
        self.send(text_data=json.dumps({'bid':bid}))
    def comment_message(self,event):
        comment=event['comment']
        self.send(text_data=json.dumps({'comment':comment}))