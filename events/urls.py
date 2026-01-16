from django.urls import path
from events.views import (
    DashboardRedirectView,
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    RSVPEventView,
)

urlpatterns = [
    # dashboard
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard'),

    # events
    path('event_list/', EventListView.as_view(), name='event_list'),
    path('event_create/', EventCreateView.as_view(), name='event_create'),
    path('event_update/<int:id>/', EventUpdateView.as_view(), name='event_update'),
    path('event_delete/<int:id>/', EventDeleteView.as_view(), name='event_delete'),
    path('event_details/<int:id>/', EventDetailView.as_view(), name='event_details'),

    # categories
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('category_create/', CategoryCreateView.as_view(), name='category_create'),
    path('category_update/<int:id>/', CategoryUpdateView.as_view(), name='category_update'),
    path('category_delete/<int:id>/', CategoryDeleteView.as_view(), name='category_delete'),

    # RSVP
    path('rsvp_event/<int:event_id>/', RSVPEventView.as_view(), name='rsvp_event'),
]