from django.dispatch import receiver
from portal.models import ChatMessage, ChatSession
from django.db.models.signals import post_save
from django_redis import get_redis_connection
from portal.features.alida_ai.alida_serializers import ChatMessageSerializer
import json


"""
    This signal is used to invalidate the Alida AI cache when a new chat message is created.
"""


@receiver([post_save], sender=ChatMessage)
def invalidate_alida_ai_signals(sender, instance, **kwargs):
    user_id = instance.session.user.id
    redis = get_redis_connection("default")
    key = f"chat:{user_id}"
    # Fetch last 10 messages from DB
    chat_session = instance.session
    chat_messages = ChatMessage.objects.filter(session=chat_session).order_by(
        "-created_at"
    )[:10]
    serializer = ChatMessageSerializer(chat_messages, many=True)
    # Clear and repopulate Redis list
    redis.delete(key)
    # Repopulate Redis with latest 10 messages in chronological order (oldest first)
    for msg in reversed(serializer.data):  # chronological order
        redis.lpush(key, json.dumps(msg))
