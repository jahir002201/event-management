from django.urls import path
from users.views import sign_in, sign_up, sign_out, activate_user, admin_dashboard, organizer_dashboard, participant_dashboard, assign_role, create_group, group_list, group_edit, group_delete, participant_list, delete_participant

urlpatterns = [
    path('sign_in/', sign_in, name='sign_in'),
    path('sign_up/', sign_up, name='sign_up'),
    path('sign_out/', sign_out, name='sign_out'),
    path('activate/<int:user_id>/<str:token>/', activate_user, name='activate_user'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('organizer_dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('participant_dashboard/', participant_dashboard, name='participant_dashboard'),
    path('assign_role/<int:user_id>/', assign_role, name='assign_role'),
    path('create_group/', create_group, name='create_group'),
    path('group_list/', group_list, name='group_list'),
    path('group_edit/<int:group_id>/', group_edit, name='group_edit'),
    path('group_delete/<int:group_id>/', group_delete, name='group_delete'),
    path('participants/', participant_list, name='participant_list'),
    path('delete_participants/<int:user_id>/', delete_participant, name='delete_participant'),
]