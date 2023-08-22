from datetime import datetime, timedelta
import openai
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.db.models import F, Q, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView, DestroyAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, SummarySerializer, ChangePasswordSerializer
import openai
import math
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Transcription, User, Summary
from .serializers import (
    TranscriptionSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserSignupSerializer,
)

class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)  # Use UserSignupSerializer here
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            password = serializer.validated_data['password']
            
            user = User.objects.create_user(email=email, name=name, password=password)
            user.generate_verification_code()  # Generate and set verification code

            subject = 'Welcome to ThoughtForest'
            verification_link = reverse('email_verification') + f'?code={user.verification_code}'
            message = f'You are about to embark on a journey, your life will never be the same. You chose to trust me, and I shall make it worth it for you. I am putting every particle in my body, every ounce of my energy, every bit of my soul into making this a meaningful experience for you. Thank you, {name} for trusting me. I will not let you down.\n\nReply to this email for feedback or a FREE voucher for one month to use this application.\n\nYou can verify your email by clicking on the following link:\n\n{verification_link}'
            from_email = 'atg271@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            subject = f'{name} has joined ThoughtForest'
            current_time = datetime.now().strftime("%H:%M:%S")
            message = f'{name} has joined ThoughtForest at {current_time}.'
            from_email = "atg271@gmail.com"
            recipient_list = [from_email]
            send_mail(subject, message, from_email, recipient_list)

            # Send the email with the verification link
            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'User created successfully'}, 
                            status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                # refresh_token = str(refresh)
                response_data = {
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TranscriptionCreateView(generics.CreateAPIView):
    serializer_class = TranscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        # if user.is_subscription_active:  # Check if the user's subscription is active
        serializer.save(user=user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transcriptions(request):
    user = request.user
    transcriptions = Transcription.objects.filter(user=user)
    serializer = TranscriptionSerializer(transcriptions, many=True)
    return Response(serializer.data)

def send_data_to_openai(data):
    openai.api_key = settings.OPENAI_API_KEY
    response = openai.Completion.create(
        engine="davinci-codex",  # Replace with the appropriate engine
        prompt=data,
        max_tokens=50  # Adjust as needed
    )

    return response.choices[0].text
class FetchAllTranscriptions(APIView):

    def calculate_num_lines(self, text):
        if len(text) == 0:
            return 0
        if len(text) <1000:
            return math.ceil(len(text)/100)
        else:
            return 15
        
    def placeholder_manipulation_function_for_transcript(self, transcript):
        num_of_lines = self.calculate_num_lines(transcript)
        prompt = "Summary of the following text in " + str(num_of_lines) + " bullet point lines, it is to be written as a journal point of view:\n\n" + transcript + "\n\nSummary:"
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response["choices"][0]["message"]["content"]

    def get(self, request):
        if request.META['REMOTE_ADDR'] == '127.0.0.1':
            today = timezone.now().date()
            transcriptions_by_week = []
            users = Transcription.objects.values('user').distinct()
            total_week_transcripts = []  # Collect all transcripts for summary
            
            for user in users:
                user_id = user['user']
                user_transcriptions = Transcription.objects.filter(user=user_id, 
                                                                   date__lte=today, 
                                                                   date__gte=today - timezone.timedelta(days=today.weekday())).order_by('date')
                
                if user_transcriptions:
                    week_start = user_transcriptions[0].date
                    week_transcripts = []
                    week_total_length = 0
                    
                    for transcription in user_transcriptions:
                        if week_start <= transcription.date < today + timezone.timedelta(days=7):
                            if transcription.transcript is not None:
                                week_transcripts.append(transcription.transcript)
                                week_total_length += len(transcription.transcript)
                                
                    if week_transcripts:
                        total_week_transcripts.extend(week_transcripts)  # Collect all transcripts
                        
            if total_week_transcripts:
                total_transcripts_summary = ' '.join(total_week_transcripts)
                summary = self.placeholder_manipulation_function_for_transcript(total_transcripts_summary)
                
                # Create or update summary entry in the Summary table for the specific user
                summary_obj, created = Summary.objects.get_or_create(user_id=user_id, date=today, defaults={'mood': 'neutral', 'summary': summary})
                if not created:
                    summary_obj.summary = summary
                    summary_obj.save()

            return Response(transcriptions_by_week)
        else:
            raise PermissionDenied("You are not allowed to access this endpoint.")

class UserDetailsView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserProfileUpdateView(UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserProfileDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class TranscriptionUpdateView(UpdateAPIView):
    serializer_class = TranscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transcription.objects.filter(user=user)
    
class TranscriptionDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transcription.objects.filter(user=user)
    
class SummaryCreateView(CreateAPIView):
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer, request):
        if request.META['REMOTE_ADDR'] == '127.0.0.1':
            serializer.save(user=self.request.user)
        else:
            raise PermissionDenied("You are not allowed to access this endpoint.")

class SummaryUpdateView(UpdateAPIView):
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Summary.objects.filter(user=user)
    
class SummaryDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Summary.objects.filter(user=user)

class SummaryRetrieveView(RetrieveAPIView):
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Summary.objects.filter(user=user)
    
class AllSummariesRetrieveView(APIView):
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        summaries = Summary.objects.filter(user=user)
        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_code(request):
    user = request.user
    access_code = request.data.get('accessCode')

    if access_code == "AUGUST":
        user.is_subscription_active = True
        user.save()
        return Response({'message': 'Subscription activated successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid access code.'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'The only journey is the one within.'})

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            user.change_password(old_password, new_password)
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.core.mail import EmailMessage

class ExportUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_data = {
            'user_details': UserSerializer(user).data,
            'transcriptions': TranscriptionSerializer(Transcription.objects.filter(user=user), many=True).data,
            'summaries': SummarySerializer(Summary.objects.filter(user=user), many=True).data,
        }
        
        # Create a JSON file containing the user's data
        import json
        user_data_json = json.dumps(user_data, indent=4)
        
        # Send the email
        subject = 'Your Data Export'
        message = 'Please find attached your requested data export.'
        from_email = 'your@email.com'
        recipient_list = [user.email]

        email = EmailMessage(subject, message, from_email, recipient_list)
        email.attach('user_data.json', user_data_json, 'application/json')
        email.send()

        return Response({'message': 'Data export requested. You will receive an email shortly.'}, status=status.HTTP_200_OK)
    

class EmailVerificationView(APIView):
    def get(self, request):

        verification_code = request.query_params.get('code')
        try:
            user = User.objects.get(verification_code=verification_code)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code.'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({'message': 'Email is already verified.'}, status=status.HTTP_200_OK)
        
        if user.verification_attempts >= 3:
            user.generate_verification_code()  # Generate a new verification code
            user.verification_attempts = 0  # Reset the verification attempts counter
            user.save()
            return Response({'message': 'Verification code expired. A new code has been sent to your email.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update verification attempts counter
        user.is_email_verified = True
        user.verification_attempts += 1
        user.save()
        return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)

class GenerateNewVerificationCodeView(APIView):
    def get(self, request):
        user = request.user  # The authenticated user
        
        # Generate a new verification code for the user
        user.generate_verification_code()
        user.save()
        
        # Send an email to the user with the new verification code
        subject = 'New Verification Code'
        verification_link = 'thoughtforest.xyz/verify' + f'?code={user.verification_code}'
        verification_url = request.build_absolute_uri(verification_link)
        message = f'Your new verification code is: {user.verification_code}<br><br>You can verify your email by clicking on the following link:<br><br><a href="{verification_url}">{verification_url}</a>'
        from_email = 'atg271@gmail.com'
        recipient_list = [user.email]
        send_mail(subject, '', from_email, recipient_list, html_message=message)
        
        return Response({'message': 'New verification code generated and sent to your email.'}, status=status.HTTP_200_OK)