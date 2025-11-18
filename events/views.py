from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.timezone import now
from datetime import datetime, date
from django.db.models import Q, Count
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm
from django.contrib import messages


# dashboard
def dashboard(request):
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=now().date()).count()
    past_events = Event.objects.filter(date__lt=now().date()).count()
    total_participants = Participant.objects.count()
    today_events = Event.objects.filter(date=now().date()).select_related('category').prefetch_related('participants')

    event_filter = request.GET.get('filter', 'today')
        
    if event_filter == 'upcoming':
        filtered_events = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')
        list_title = "Upcoming Events"
    elif event_filter == 'past':
        filtered_events = Event.objects.filter(date__lt=now().date()).select_related('category').order_by('-date')
        list_title = "Past Events"
    elif event_filter == 'all':
        filtered_events = Event.objects.all().select_related('category').order_by('-date')
        list_title = "All Events"
    else:
        filtered_events = today_events
        list_title = "Today's Events"

    context = {
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "total_participants": total_participants,
        "today_events": today_events,
        "filtered_events": filtered_events,
        "list_title": list_title,
    }
    return render(request, 'events/dashboard.html', context)

# events
def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants').all()
    context = {'events': events}
    return render(request, 'events/event_list.html', context)

def event_details(request, id):
    event = Event.objects.select_related('category').prefetch_related('participants').get(id=id)
    return render(request, 'events/event_details.html', {"event": event})

def event_home(request):
    events_query = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')

    search_keyword = request.GET.get('search')
    start_date2 = request.GET.get('start_date')
    end_date2 = request.GET.get('end_date')

    datefilter = False

    if start_date2 and end_date2:
        try:
            start = datetime.strptime(start_date2, '%d/%m/%Y').date()
            end = datetime.strptime(end_date2, '%d/%m/%Y').date()
            if start <= end:
                events_query = events_query.filter(date__range=(start, end))
                datefilter = True
            else:
                 messages.error(request, "Error: The end date cannot be before the start date.")

        except ValueError:
            messages.error(request, "Error: Invalid date format. Please use DD/MM/YYYY.")

    if search_keyword:
        events_query = events_query.filter(Q(name__icontains=search_keyword) | Q(location__icontains=search_keyword))

    category_id = request.GET.get('category')

    if category_id:
        events_query = events_query.filter(category__id=category_id)

    if search_keyword or category_id or datefilter:
        filtered_events = events_query.prefetch_related('participants')
    else:
        filtered_events = events_query[:12].prefetch_related('participants')

    categories = Category.objects.all()
    total_events = Event.objects.count()
    total_upcoming = Event.objects.filter(date__gte=now().date()).count()
    featured_event = events_query.first() 
    
    context = {
        'filtered_events': filtered_events,
        'categories': categories,
        'total_events': total_events,
        'total_results': filtered_events.count(),
        'total_upcoming': total_upcoming,
        'search_keyword': search_keyword,
        'category_id': category_id,
        'featured_event': featured_event,
        'start_date': start_date2, 
        'end_date': end_date2,
    }
    return render(request, 'events/event_home.html', context)

def event_create(request):
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    return render(request, "form/event_form.html", {"form": form})


def event_update(request, id):
    event = Event.objects.get(id=id)
    form = EventForm(instance=event)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_list')
    return render(request, "form/event_form.html", {"form": form})

def event_delete(request, id):
    event = Event.objects.get(id=id)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully")
        return redirect('event_list')

    messages.error(request, "Something went wrong")
    return redirect('event_list')

# category
def category_list(request):
    categories = Category.objects.annotate(num_events=Count('events')).all()
    context = {'categories': categories}
    return render(request, 'events/category_list.html', context)

def category_create(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect('category_list')
    return render(request, "form/category_form.html", {"form": form})

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

def category_delete(request, id):
    category = Category.objects.get(id=id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully")
        return redirect('category_list')
    messages.error(request, "Something went wrong")
    return redirect('category_list')

# participant
def participant_list(request):
    participants = Participant.objects.prefetch_related('events').all()
    context = {'participants': participants}
    return render(request, 'events/participant_list.html', context)

def participant_create(request):
    form = ParticipantForm()
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant created successfully!")
            return redirect('participant_list')
    return render(request, "form/participant_form.html", {"form": form})


def participant_update(request, id):
    participant = Participant.objects.get(id=id)
    form = ParticipantForm(instance=participant)
    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant updated successfully!")
            return redirect('participant_list')
    return render(request, "form/participant_form.html", {"form": form})


def participant_delete(request, id):
    participant = Participant.objects.get(id=id)
    if request.method == "POST":
        participant.delete()
        messages.success(request, "Participant deleted successfully!")
        return redirect('participant_list')
    messages.error(request, "Something went wrong")
    return redirect('participant_list')