from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.timezone import now
from events.models import Event, Category
from events.forms import EventForm, CategoryForm
import os
from django.conf import settings
from django.db.models import Count


# Role mixins
class AdminOrganizerRequiredMixin(UserPassesTestMixin):
    login_url = 'no_permission'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()


class ParticipantRequiredMixin(UserPassesTestMixin):
    login_url = 'no_permission'

    def test_func(self):
        return self.request.user.groups.filter(name='Participant').exists()


# Dashboard redirect based on role
class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        if user.is_superuser or user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif user.groups.filter(name='Organizer').exists():
            return redirect('organizer_dashboard')
        else:
            return redirect('participant_dashboard')


# Event List
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.select_related('category').order_by('date')


# Event Details
class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_details.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Event.objects.select_related('category').prefetch_related('participants')


# Create Event
class EventCreateView(LoginRequiredMixin, AdminOrganizerRequiredMixin, View):
    template_name = 'form/event_form.html'

    def get(self, request):
        form = EventForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
        return render(request, self.template_name, {'form': form})


# Update Event
class EventUpdateView(LoginRequiredMixin, AdminOrganizerRequiredMixin, View):
    template_name = 'form/event_form.html'

    def get(self, request, id):
        event = Event.objects.get(id=id)
        form = EventForm(instance=event)
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        event = Event.objects.get(id=id)
        old_image = event.image
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            # Delete old image if replaced
            if 'image' in request.FILES and old_image and old_image.name != 'event_images/default_img.jpg':
                old_image_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_list')
        return render(request, self.template_name, {'form': form})


# Delete Event
class EventDeleteView(LoginRequiredMixin, AdminOrganizerRequiredMixin, DeleteView):
    model = Event
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('event_list')

    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        # Delete image file
        if event.image and event.image.name != 'event_images/default_img.jpg':
            image_path = os.path.join(settings.MEDIA_ROOT, event.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
        messages.success(request, "Event deleted successfully")
        return super().delete(request, *args, **kwargs)


# Category List
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(num_events=Count('events')).all()


# Category Create
class CategoryCreateView(LoginRequiredMixin, AdminOrganizerRequiredMixin, View):
    template_name = 'form/category_form.html'

    def get(self, request):
        form = CategoryForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect('category_list')
        return render(request, self.template_name, {'form': form})


# Category Update
class CategoryUpdateView(LoginRequiredMixin, AdminOrganizerRequiredMixin, View):
    template_name = 'form/category_form.html'

    def get(self, request, id):
        category = Category.objects.get(id=id)
        form = CategoryForm(instance=category)
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        category = Category.objects.get(id=id)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('category_list')
        return render(request, self.template_name, {'form': form})


# Category Delete
class CategoryDeleteView(LoginRequiredMixin, AdminOrganizerRequiredMixin, DeleteView):
    model = Category
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully")
        return super().delete(request, *args, **kwargs)


# RSVP Event
class RSVPEventView(LoginRequiredMixin, ParticipantRequiredMixin, View):
    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        user = request.user
        if user in event.participants.all():
            messages.warning(request, "You have already RSVPed to this event.")
        else:
            event.participants.add(user)
            messages.success(request, "RSVP successful! A confirmation email has been sent.")
        return redirect('home')