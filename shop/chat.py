from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import requests
import json
import time

redis_client = settings.REDIS_CLIENT



class ChatView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        message = request.data.get("message")
        thread_id = request.data.get("thread_id")
        
        if not message:
            return Response({"error": "message is required"}, status=400)
        if not thread_id:
            return Response({"error": "thread_id is required"}, status=400)
        
        
        request.session.create()
        request.session["created_at"] = int(time.time())
        request.session["thread_id"] = str(thread_id)
        request.session.save()
        
        
        
        chat_key = f"chat:{thread_id}"  
        current_length = redis_client.llen(chat_key)
        
        # SAVE USER MESSAGE
        user_message = {
            "id": current_length + 1,
            "sender": "user",
            "message": message
        }
        redis_client.rpush(chat_key, json.dumps(user_message))
        
        
        response_data = {
            "thread_id": thread_id if thread_id else "dfshfwf1545fiewifweifiwe",
            "message": message
        }
        
        try:
            ai_response = requests.post("http://10.10.7.75:7777/chat", json=response_data, timeout=10)
            ai_response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
            ai_data = ai_response.json()
            bot_reply = ai_data.get("reply", "")
        except requests.exceptions.RequestException:
            # This will catch connection errors, timeouts, and HTTP errors
            return Response({"error": "AI server is Busy"}, status=400)

        
        
        bot_message = {
            "id": current_length + 2,
            "sender": "bot",
            "message": bot_reply.strip('"')
        }
        redis_client.rpush(chat_key, json.dumps(bot_message))
        
        ai_response = {
            "thread_id": thread_id,
            "ai_response": ai_data
        }

        return Response(ai_response)



# class ChatView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         message = request.data.get("message")
#         thread_id = request.data.get("thread_id")
        
#         if not message:
#             return Response({"error": "message is required"}, status=400)
#         if not thread_id:
#             return Response({"error": "thread_id is required"}, status=400)
        
#         # Get session creation time
#         created_at = request.session.get("created_at")
#         duration_time = int(time.time()) - created_at if created_at else 0
        
        
#         # Flush session only if it exists and duration is > 1 day
#         if request.session.session_key and duration_time > 86400: 
#             request.session.flush()
            
#             # Create a new session after flush
#             request.session.create()
#             request.session["created_at"] = int(time.time())
            
#         else:
#             # If session didn't flush, make sure created_at exists
#             if not created_at:
#                 request.session.create()
#                 request.session["created_at"] = int(time.time())
        
        
#         chat_key = f"chat:{request.session.session_key}"  
#         current_length = redis_client.llen(chat_key)
        
#         # SAVE USER MESSAGE
#         user_message = {
#             "id": current_length + 1,
#             "sender": "user",
#             "message": message
#         }
#         redis_client.rpush(chat_key, json.dumps(user_message))
        
        
#         response_data = {
#             "thread_id": thread_id if thread_id else "dfshfwf1545fiewifweifiwe",
#             "message": message
#         }
        
#         return Response(response_data)
        
        # ai_response = requests.post("http://10.10.7.75:7777/chat", json=response_data)
        # ai_data = ai_response.json()
        # bot_reply = ai_data.get("reply", "")
        
        
        # bot_message = {
        #     "id": current_length + 2,
        #     "sender": "bot",
        #     "message": bot_reply.strip('"')
        # }
        # redis_client.rpush(chat_key, json.dumps(bot_message))

        # return Response({
        #     "thread_id": request.session.session_key,
        #     "Ai_response": ai_data
        # })
        
        
class ConversationlistView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, thread_id):
        chat_key = f"chat:{thread_id}"
        conversation = [
            json.loads(item)
            for item in redis_client.lrange(chat_key, 0, -1)
        ]
        
        return Response({
            "thread_id": thread_id,
            "Full_conversation": conversation
        })