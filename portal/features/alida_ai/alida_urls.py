from django.urls import path
from portal.features.alida_ai import alida_views as views

# URL patterns for the Alida AI chatbot
urlpatterns = [
    path("chat/", views.ChatbotAPIView.as_view(), name="alida_chat"),
    path(
        "chat-history/", views.GetChatHistory.as_view(), name="alida_chat_conversation"
    ),
]
