from django.urls import path

from .views import (
    FetchAllTranscriptions,
    TranscriptionCreateView,
    UserLoginView,
    UserSignupView,
    get_transcriptions,
    UserDetailsView,
    UserProfileDeleteView,
    UserProfileUpdateView,
    TranscriptionUpdateView,
    TranscriptionDeleteView,
    SummaryCreateView,
    SummaryUpdateView,
    SummaryDeleteView,
    SummaryRetrieveView,
    AllSummariesRetrieveView,
    check_code,
    ChangePasswordView,
    hello_world
)

urlpatterns = [
    path('', hello_world, name='hello_world'),
    path('signup/', UserSignupView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('add-transcription/', TranscriptionCreateView.as_view(), 
         name='add_transcription'),
    path('get-transcriptions/', get_transcriptions, name='get_transcriptions'),
    # path('fetch-all/', FetchAllTranscriptions.as_view(), name='fetch_all_transcriptions'),
    path('user-details/', UserDetailsView.as_view(), name='user_details'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('user-profile/update/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('user-profile/delete/', UserProfileDeleteView.as_view(), name='user_profile_delete'),
    path('transcription/<int:pk>/update/', TranscriptionUpdateView.as_view(), name='transcription_update'),
    path('transcription/<int:pk>/delete/', TranscriptionDeleteView.as_view(), name='transcription_delete'),
    path('add-summary/', SummaryCreateView.as_view(), name='add_summary'),
    path('summary/<int:pk>/update/', SummaryUpdateView.as_view(), name='summary_update'),
    path('summary/<int:pk>/delete/', SummaryDeleteView.as_view(), name='summary_delete'),
    path('summary/<int:pk>/retrieve/', SummaryRetrieveView.as_view(), name='summary_retrieve'),
    path('all-summaries/', AllSummariesRetrieveView.as_view(), name='all_summaries'),
    path('check-code/', check_code, name='check_code'),
]