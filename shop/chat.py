from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import requests
import json

redis_client = settings.REDIS_CLIENT


class ChatAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        message = request.data.get("message")

        if not message:
            return Response({"error": "message is required"}, status=400)

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        # Use session ID as thread_id
        thread_id = request.session.session_key

        # Redis key
        chat_key = f"chat:{thread_id}"

        # Get current conversation length to generate IDs
        current_length = redis_client.llen(chat_key)

        # Save user message
        user_message = {
            "id": current_length + 1,
            "sender": "user",
            "message": message
        }
        redis_client.rpush(chat_key, json.dumps(user_message))

        # Send to AI endpoint
        response_data = {
            "thread_id": thread_id,
            "message": message
        }
        ai_response = requests.post('http://10.10.7.75:7777/chat', json=response_data)
        ai_data = ai_response.json()
        bot_reply = ai_data.get("reply", "")

        # Save bot message
        bot_message = {
            "id": current_length + 2,
            "sender": "bot",
            "message": bot_reply.strip('"')  # remove extra quotes if present
        }
        redis_client.rpush(chat_key, json.dumps(bot_message))

        # Get full conversation
        conversation = [
            json.loads(item)
            for item in redis_client.lrange(chat_key, 0, -1)
        ]

        res_data = {
            "Ai_response": ai_data,
            "thread_id": thread_id,
            "Full_conversation": conversation            
        }

        return Response(res_data)





class ClearChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Use provided thread_id or current session
        thread_id = request.data.get("thread_id") or request.session.session_key

        if not thread_id:
            return Response({"error": "thread_id or active session is required"}, status=400)

        chat_key = f"chat:{thread_id}"

        # Delete the Redis key
        deleted_count = redis_client.delete(chat_key)

        if deleted_count:
            return Response({"success": f"Chat cleared for thread_id {thread_id}"})
        else:
            return Response({"info": f"No chat found for thread_id {thread_id}"})