from os import read
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    """
    Serializer for chat messages sent to the AI assistant.
    """

    sender = serializers.CharField(
        help_text="Identifier of the user sending the message",
        read_only=True,
    )
    content = serializers.CharField(
        required=True, help_text="User's message to the AI assistant"
    )


class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer for responses from the AI assistant.
    """

    response = serializers.CharField(help_text="AI assistant's response")
    created_at = serializers.DateTimeField(help_text="Timestamp of the response")
