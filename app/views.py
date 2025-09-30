from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Ticket, Trader, Transaction
from django.utils.crypto import get_random_string




User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """
    Functional view to register a new user with Django password validation
    """
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")

    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "User with this email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Run Django’s password validators
    try:
        validate_password(password)
    except DjangoValidationError as e:
        return Response(
            {"error": e.messages},  # returns a list of validation messages
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create user if password is valid
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "token": token.key,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    """
    Functional view to login a user
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    


    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "token": token.key,
        },
        status=status.HTTP_200_OK,
    )


# Tickets
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def tickets_view(request):
    if request.method == "POST":
        # Create a new ticket
        subject = request.data.get("subject")
        category = request.data.get("category")
        description = request.data.get("description")

        if not subject or not category or not description:
            return Response(
                {"error": "All fields (subject, category, description) are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket = Ticket.objects.create(
            user=request.user,
            subject=subject,
            category=category,
            description=description,
        )

        return Response(
            {
                "message": "Ticket created successfully",
                "ticket": {
                    "id": ticket.id,
                    "subject": ticket.subject,
                    "category": ticket.category,
                    "description": ticket.description,
                    "user": ticket.user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "GET":
        # Get tickets for logged-in user
        tickets = Ticket.objects.filter(user=request.user).values(
            "id", "subject", "category", "description"
        )
        return Response(
            {"tickets": list(tickets)},
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_user_profile(request):
    """
    Retrieve the profile of the logged-in user
    """
    user = request.user

    return Response(
        {
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "free_margin": user.free_margin,
                "user_funds": user.user_funds,
                "balance": user.balance,
                "equity": user.equity,
                "margin_level": user.margin_level,
                "account_id": user.account_id,
            }
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transactions_view(request):
    if request.method == "POST":
        transaction_type = request.data.get("transaction_type")
        amount = request.data.get("amount")
        description = request.data.get("description", "")

        if not transaction_type or not amount:
            return Response(
                {"error": "transaction_type and amount are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if transaction_type not in ["deposit", "withdrawal"]:
            return Response(
                {"error": "Invalid transaction type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {"error": "Amount must be a number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a unique reference
        reference = get_random_string(12)

        transaction = Transaction.objects.create(
            user=request.user,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            reference=reference,
            status="pending",  # default
        )

        return Response(
            {
                "message": "Transaction created successfully",
                "transaction": {
                    "id": transaction.id,
                    "transaction_type": transaction.transaction_type,
                    "amount": str(transaction.amount),
                    "status": transaction.status,
                    "reference": transaction.reference,
                    "description": transaction.description,
                    "created_at": transaction.created_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    # GET request → return all transactions for logged-in user
    transactions = Transaction.objects.filter(user=request.user).values(
        "id", "transaction_type", "amount", "status", "reference", "description", "created_at"
    )

    return Response(
        {"transactions": list(transactions)},  # [] if none exist
        status=status.HTTP_200_OK,
    )





