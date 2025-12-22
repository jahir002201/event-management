from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.timezone import now
from datetime import datetime, date
from django.db.models import Q, Count
from events.models import Event, Category
from events.forms import EventForm, CategoryForm
from django.contrib import messages
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    else:
        return redirect('participant_dashboard')
@login_required
def event_list(request):
    events = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')
    context = {'events': events}
    return render(request, 'events/event_list.html', context)

def event_details(request, id):
    event = Event.objects.select_related('category').prefetch_related('participants').get(id=id)
    return render(request, 'events/event_details.html', {"event": event})

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def event_create(request):
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    return render(request, "form/event_form.html", {"form": form})

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def event_update(request, id):
    event = Event.objects.get(id=id)
    old_image = event.image
    form = EventForm(instance=event)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():

            if 'image' in request.FILES:
                if old_image and old_image.name != 'event_images/default_img.jpg':
                    old_image_path = os.path.join(settings.MEDIA_ROOT, old_image.name)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_list')
    return render(request, "form/event_form.html", {"form": form})

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def event_delete(request, id):
    event = Event.objects.get(id=id)
    if request.method == "POST":

        if event.image and event.image.name != 'event_images/default_img.jpg':
            image_path = os.path.join(settings.MEDIA_ROOT, event.image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)

        event.delete()
        messages.success(request, "Event deleted successfully")
        return redirect('event_list')

    messages.error(request, "Something went wrong")
    return redirect('event_list')

@login_required
def category_list(request):
    categories = Category.objects.annotate(num_events=Count('events')).all()
    context = {'categories': categories}
    return render(request, 'events/category_list.html', context)

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def category_create(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect('category_list')
    return render(request, "form/category_form.html", {"form": form})

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def category_update(request, id):
    category = Category.objects.get(id=id)
    form = CategoryForm(instance=category)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('category_list')
    return render(request, "form/category_form.html", {"form": form})

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def category_delete(request, id):
    category = Category.objects.get(id=id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully")
        return redirect('category_list')
    messages.error(request, "Something went wrong")
    return redirect('category_list')

@login_required
def rsvp_event(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user
    if user in event.participants.all():
        messages.warning(request, "You have already RSVPed to this event.")
    else:
        event.participants.add(user)
        messages.success(request, "RSVP successful! A confirmation email has been sent.")

    return redirect('home')