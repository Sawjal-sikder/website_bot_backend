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

        # Save session
        request.session["created_at"] = int(time.time())
        request.session["thread_id"] = str(thread_id)
        request.session.save()

        chat_key = f"chat:{thread_id}"
        current_length = redis_client.llen(chat_key)

        # Save user message
        user_message = {
            "id": current_length + 1,
            "sender": "user",
            "message": message
        }
        redis_client.rpush(chat_key, json.dumps(user_message))

        # Call AI SERVER
        try:
            ai_response_raw = requests.post(
                "https://ai.orderwithpluto.com/chat",
                json={"thread_id": thread_id, "message": message},
                timeout=100
            )
            ai_response_raw.raise_for_status()

            # Parse AI response
            ai_data = ai_response_raw.json()
            bot_reply = ai_data.get("reply", "No reply received")

        except requests.exceptions.Timeout:
            return Response({"error": "AI server timeout"}, status=504)

        except requests.exceptions.RequestException:
            return Response({"error": "AI server busy"}, status=503)

        # Save bot reply to Redis
        bot_message = {
            "id": current_length + 2,
            "sender": "bot",
            "message": bot_reply
        }
        redis_client.rpush(chat_key, json.dumps(bot_message))

        output = {
            "thread_id": thread_id,
            "ai_response": ai_data
        }

        return Response(output)


        
        
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