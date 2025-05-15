import json
import logging
import os
from django.utils import timezone
from django.db import models
from django.conf import settings
import redis
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django_redis import get_redis_connection
import json

from portal.features.alida_ai.alida_serializers import (
    ChatMessageSerializer,
    ChatResponseSerializer,
)
from portal.models import (
    Account,
    Vehicle,
    WaterBill,
    ParkingTicket,
    ChatSession,
    ChatMessage,
)


# Configure logging
logger = logging.getLogger(__name__)

# Check if OpenAI is installed
try:
    import openai
except ImportError:
    logger.error(
        "OpenAI package not installed. Please install it using 'pip install openai'"
    )


redis = get_redis_connection("default")
# Initialize Redis connection


class ChatbotAPIView(APIView):
    """
    API view for interacting with the OpenAI-powered chatbot.
    The chatbot can provide information about user's water bills and parking tickets.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChatMessageSerializer,
        responses={200: ChatResponseSerializer},
        parameters=[
            OpenApiParameter(
                name="X-Cache-Control",
                description="Cache control header",
                required=False,
                type=str,
            )
        ],
        description="Send a message to the AI assistant to get information about water bills or parking tickets.",
    )
    def post(self, request, *args, **kwargs):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user_message = serializer.validated_data["content"]

        # Get or create a chat session (could use session/cookie or always create new)
        session, _ = ChatSession.objects.get_or_create(user=user)

        # Save user message
        user_msg_obj = ChatMessage.objects.create(
            session=session,
            sender="user",
            content=user_message,
        )

        try:
            # Get context data for the current user
            context_data = self._get_user_context_data(request.user)

            # Generate system message with context
            system_message = self._generate_system_message(context_data)

            # Call OpenAI API
            response_content = self._call_openai_api(user_message, system_message)

            # Save AI response
            ai_msg_obj = ChatMessage.objects.create(
                session=session,
                sender="ai",
                content=response_content,
            )

            # Cache both user and ai messages in Redis only if not already present
            key = f"chat:{user.id}"
            user_msg_data = ChatMessageSerializer(user_msg_obj).data
            ai_msg_data = ChatMessageSerializer(ai_msg_obj).data

            # Prevent duplicates by checking the latest message in Redis
            last_msgs = redis.lrange(key, 0, 1)
            last_contents = [json.loads(m).get("content") for m in last_msgs]
            if user_msg_data["content"] not in last_contents:
                redis.lpush(key, json.dumps(user_msg_data))
            if ai_msg_data["content"] not in last_contents:
                redis.lpush(key, json.dumps(ai_msg_data))
            redis.ltrim(key, 0, 59)
            redis.expire(key, 60 * 15)
            # Save the chat session to the database

            # session.save()

            # Format and return response
            response_data = {"response": response_content, "created_at": timezone.now()}

            response = Response(response_data)

            # Add cache control headers for optimization
            response["Cache-Control"] = "private, max-age=0, no-cache"

            return response

        except Exception as e:
            logger.error(f"Error processing chatbot request: {str(e)}")
            return Response(
                {"error": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_user_context_data(self, user):
        """
        Retrieve context data for the current user including water bills and parking tickets.
        This data will be used to provide personalized responses.
        """
        context = {}

        # Get water bills data
        water_bills = WaterBill.objects.filter(user=user).order_by("-created_at")[:5]
        if water_bills.exists():
            context["water_bills"] = []
            for bill in water_bills:
                bill_data = {
                    "bill_number": bill.bill_number,
                    "billing_period": (
                        bill.billing_period.bill_date.strftime("%Y-%m-%d")
                        if bill.billing_period
                        else None
                    ),
                    "due_date": (
                        bill.billing_period.due_date.strftime("%Y-%m-%d")
                        if bill.billing_period and bill.billing_period.due_date
                        else None
                    ),
                    "total_amount": bill.total_amount,
                    "amount_paid": bill.amount_paid,
                    "remaining_balance": bill.remaining_balance,
                    "payment_status": bill.payment_status,
                }

                # Add consumption data if available
                if bill.water_usage:
                    bill_data["consumption"] = bill.water_usage.consumption

                context["water_bills"].append(bill_data)

        # Get parking tickets data
        parking_tickets = ParkingTicket.objects.filter(user=user).order_by(
            "-issued_at"
        )[:10]
        if parking_tickets.exists():
            context["parking_tickets"] = []
            for ticket in parking_tickets:
                ticket_data = {
                    "ticket_number": ticket.ticket_number,
                    "ticket_date": (
                        ticket.issued_at.strftime("%Y-%m-%d")
                        if ticket.issued_at
                        else None
                    ),
                    "amount": ticket.amount,
                    "status": ticket.status,
                }
                context["parking_tickets"].append(ticket_data)

        vehicles = Vehicle.objects.filter(owner=user).order_by("-registered_at")[:5]
        if vehicles.exists():
            context["vehicles"] = []
            for vehicle in vehicles:
                vehicle_data = {
                    "license_plate": vehicle.plate_number,
                    "make": vehicle.brand,
                    "model": vehicle.model,
                    "vehicle_type": vehicle.vehicle_type,
                    "color": vehicle.color,
                    "approval_status": vehicle.approval_status,
                    "is_active": vehicle.is_active,
                    "registered_at": (
                        vehicle.registered_at.strftime("%Y-%m-%d")
                        if vehicle.registered_at
                        else None
                    ),
                }
                context["vehicles"].append(vehicle_data)

        accounts = Account.objects.filter(user=user).order_by("-created_at")[:5]
        if accounts.exists():
            context["accounts"] = []
            for account in accounts:
                account_data = {
                    "account_number": account.account_number,
                    "water_meter_number": account.water_meter_number,
                    "created_at": (
                        account.created_at.strftime("%Y-%m-%d")
                        if account.created_at
                        else None
                    ),
                }
                context["accounts"].append(account_data)

        return context

    def _generate_system_message(self, context_data):
        """
        Generate a system message with user context data to guide the AI's responses.
        """
        system_message = (
            "You are Alida, an AI assistant for the City Council Portal. "
            "You help users by providing information about their water bills and parking tickets. "
            "Be concise, helpful, and only respond to queries related to the user's data. "
            "If asked about something outside the provided context, politely explain that "
            "you can only assist with information about their water bills, vehicles, accounts and parking tickets."
            "Offer suggestions for how they can find more information if needed."
            "You can also provide information about the user's vehicles and accounts."
            "If the user asks about their water bill, provide details about the most recent bill, including "
            "the billing period, due date, total amount, amount paid, remaining balance, and payment status. "
            "If the user asks about their parking tickets, provide details about the most recent tickets, including "
            "the ticket number, ticket date, amount, and status. "
            "If the user asks about their vehicles, provide details about the most recent vehicles, including "
            "the license plate, make, model, vehicle type, color, approval status, is_active status, "
            "registered_at date, and city registered. "
            "If the user asks about their accounts, provide details about the most recent accounts, including "
            "the account number, property, water meter number, and created_at date."
            "Try to explain in simple terms and avoid technical jargon. "
            "Try to be as helpful as possible, but do not provide any information outside of the user's data."
        )

        # Add context data to the system message
        if context_data:
            system_message += "\n\nUser's data:"
            system_message += json.dumps(context_data, indent=2)
        else:
            system_message += "\n\nNo data available for this user."

        return system_message

    def _call_openai_api(self, user_message, system_message):
        """
        Call the OpenAI API to generate a response based on the user's message and context.
        """
        # Check if OPENAI_API_KEY is set
        openai_api_key = os.environ.get(
            "OPENAI_API_KEY", getattr(settings, "OPENAI_API_KEY", None)
        )
        if not openai_api_key:
            logger.error(
                "OpenAI API key not found in environment variables or settings"
            )
            return "I'm sorry, the AI service is currently unavailable. Please try again later."

        try:
            # Initialize the OpenAI client
            client = openai.OpenAI(api_key=openai_api_key)

            # Make API call
            response = client.chat.completions.create(
                model="gpt-4.1-2025-04-14",  # You can change this to a different model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            # Extract and return the response content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return "I couldn't generate a response. Please try again."

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Please try again later."


class GetChatHistory(APIView):
    """
    API view to retrieve chat history for a user.
    """

    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @method_decorator(cache_control(private=True, max_age=60 * 15))  # Cache control
    @extend_schema(
        responses={200: ChatMessageSerializer(many=True)},
        description="Retrieve the chat history for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="X-Cache-Control",
                description="Cache control header",
                required=False,
                type=str,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        redis = get_redis_connection("default")
        key = f"chat:{user.id}"

        # Try to get messages from Redis
        redis_msgs = redis.lrange(key, 0, -1)
        if redis_msgs:
            # Redis returns newest first, reverse for chronological order
            messages = [json.loads(m) for m in reversed(redis_msgs)]
            # Remove duplicates by (sender, content, created_at)
            seen = set()
            unique_msgs = []
            for msg in messages:
                msg_id = (msg.get("sender"), msg.get("content"), msg.get("created_at"))
                if msg_id not in seen:
                    seen.add(msg_id)
                    unique_msgs.append(msg)
            formatted = [
                {
                    "sender": msg.get("sender"),
                    "content": msg.get("content"),
                    "created_at": msg.get("created_at"),
                }
                for msg in unique_msgs
            ]
            return Response(formatted, status=status.HTTP_200_OK)

        # Fallback to DB if Redis empty
        chat_session = ChatSession.objects.filter(user=user).first()
        if not chat_session:
            return Response([], status=status.HTTP_200_OK)

        chat_messages = ChatMessage.objects.filter(session=chat_session).order_by(
            "-created_at"
        )[:10]
        serializer = ChatMessageSerializer(chat_messages, many=True)
        # Only cache if Redis is empty
        if not redis.lrange(key, 0, -1):
            for msg in serializer.data:
                redis.lpush(key, json.dumps(msg))
            redis.ltrim(key, 0, 9)
        formatted = [
            {
                "sender": msg["sender"],
                "content": msg["content"],
                "created_at": msg["created_at"],
            }
            for msg in reversed(serializer.data)
        ]
        return Response(formatted, status=status.HTTP_200_OK)
