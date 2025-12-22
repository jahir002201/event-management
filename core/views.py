from django.shortcuts import render
from django.utils.timezone import now
from datetime import datetime
from django.db.models import Q
from events.models import Event, Category
from django.contrib import messages

def home(request):
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
    return render(request, 'home.html', context)

def no_permission(request):
    return render(request, 'no_permission.html')