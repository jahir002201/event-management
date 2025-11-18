from django.urls import path
from events.views import dashboard, event_list, event_home, event_details, event_create, event_update, event_delete, category_list, category_create, category_update, category_delete, participant_list, participant_create, participant_update, participant_delete

urlpatterns = [
    # dashboard
    path('dashboard/', dashboard, name='dashboard'),
    # events
    path('event_list/', event_list, name='event_list'),
    path('event_create/', event_create, name='event_create'),
    path('event_update/<int:id>/', event_update, name='event_update'),
    path('event_delete/<int:id>/', event_delete, name='event_delete'),
    path('', event_home, name='event_home'),
    path('event_details/<int:id>/', event_details, name='event_details'),
    # category
    path('category_list/', category_list, name='category_list'),
    path('category_create/', category_create, name='category_create'),
    path('category_update/<int:id>/', category_update, name='category_update'),
    path('category_delete/<int:id>/', category_delete, name='category_delete'),
    # participant
    path('participant_list/',participant_list, name='participant_list'),
    path('participant_create/', participant_create, name='participant_create'),
    path('participant_update/<int:id>/', participant_update, name='participant_update'),
    path('participant_delete/<int:id>/', participant_delete, name='participant_delete'),
]