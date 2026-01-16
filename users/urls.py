from django.urls import path
from users.views import (
    SignInView, SignUpView, SignOutView, ActivateUserView,
    AdminDashboardView, OrganizerDashboardView, ParticipantDashboardView,
    AssignRoleView, CreateGroupView, GroupListView, GroupEditView, GroupDeleteView,
    ParticipantListView, DeleteParticipantView,
    ProfileView, EitProfileView, PasswordChange,
    CustomPasswordResetDoneView, CustomPasswordResetView, CustomPasswordResetConfirmView
)

urlpatterns = [
    # Authentication
    path('sign_in/', SignInView.as_view(), name='sign_in'),
    path('sign_up/', SignUpView.as_view(), name='sign_up'),
    path('sign_out/', SignOutView.as_view(), name='sign_out'),
    path('activate/<int:user_id>/<str:token>/', ActivateUserView.as_view(), name='activate_user'),

    # Dashboards
    path('admin_dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('organizer_dashboard/', OrganizerDashboardView.as_view(), name='organizer_dashboard'),
    path('participant_dashboard/', ParticipantDashboardView.as_view(), name='participant_dashboard'),

    # Roles & Groups
    path('assign_role/<int:user_id>/', AssignRoleView.as_view(), name='assign_role'),
    path('create_group/', CreateGroupView.as_view(), name='create_group'),
    path('group_list/', GroupListView.as_view(), name='group_list'),
    path('group_edit/<int:group_id>/', GroupEditView.as_view(), name='group_edit'),
    path('group_delete/<int:group_id>/', GroupDeleteView.as_view(), name='group_delete'),

    # Participants
    path('participants/', ParticipantListView.as_view(), name='participant_list'),
    path('delete_participants/<int:user_id>/', DeleteParticipantView.as_view(), name='delete_participant'),

    # Profile & Password
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-profile/', EitProfileView.as_view(), name='eit-profile'),
    path('change-password/', PasswordChange.as_view(), name='change-password'),
    path('password-change/done/', CustomPasswordResetDoneView.as_view(), name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]