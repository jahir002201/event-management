from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, logout
from users.forms import CustomRegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from events.models import Event, Category
from django.db.models import Count
from django.utils.timezone import now
from users.forms import CreateGroupForm
from django.contrib.auth.decorators import login_required, user_passes_test


def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def sign_up(request):
    form = CustomRegistrationForm()

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            group = Group.objects.get(name='Participant')
            user.groups.add(group)
            messages.success(request, "Registration successful. Please check your email to activate your account.")
            return redirect('sign_in')

    return render(request, 'registration/register.html', {'form': form})

def sign_in(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Account is not active. Please check your email to activate your account.")
                return redirect('sign_in')
            login(request, user)
            return redirect('home')

    return render(request, 'registration/login.html', {'form': form})

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign_in')

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully!")
            return redirect('sign_in')
        else:
            return HttpResponse("Invalid token")
    except User.DoesNotExist:
        return HttpResponse("User does not exist")

@user_passes_test(is_admin, login_url='no_permission')
def admin_dashboard(request):

    users = User.objects.prefetch_related('groups')

    for user in users:
        user.role = user.groups.first().name if user.groups.exists() else "None"

    context = {
        'total_users': User.objects.count(),
        'total_events': Event.objects.count(),
        'total_categories': Category.objects.count(),
        'total_rsvps': Event.objects.aggregate(
            total=Count('participants')
        )['total'],
        'users': users,
        'groups': Group.objects.all(),
    }

    return render(request, 'admin/admin.html', context)

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Organizer']).exists(), login_url='no_permission')
def organizer_dashboard(request):

    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=now().date()).count()
    past_events = Event.objects.filter(date__lt=now().date()).count()
    total_participants = Event.objects.aggregate(total_participants=Count('participants'))['total_participants']
    today_events = Event.objects.filter(date=now().date()).select_related('category').prefetch_related('participants')

    event_filter = request.GET.get('filter', 'today')
        
    if event_filter == 'upcoming':
        filtered_events = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')
        list_title = "Upcoming Events"
    elif event_filter == 'past':
        filtered_events = Event.objects.filter(date__lt=now().date()).select_related('category').order_by('-date')
        list_title = "Past Events"
    elif event_filter == 'all':
        filtered_events = Event.objects.all()
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

    return render(request, 'admin/organizer.html', context)

@user_passes_test(lambda u: u.groups.filter(name__in=['Admin','Participant']).exists(), login_url='no_permission')
def participant_dashboard(request):

    events = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')
    context = {
        'events': events,
    }

    return render(request, 'admin/participant.html', context)

@user_passes_test(is_admin, login_url='no_permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        role_id = request.POST.get('role_id')
        group = Group.objects.get(id=role_id)

        user.groups.clear()
        user.groups.add(group)

        messages.success(request,f"{user.username} assigned to {group.name}")
    return redirect('dashboard')

@user_passes_test(is_admin, login_url='no_permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('group_list')
    return render(request, 'admin/create_group.html', {'form': form})

@user_passes_test(is_admin, login_url='no_permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'admin/group_list.html', {'groups': groups})

@user_passes_test(is_admin, login_url='no_permission')
def group_edit(request, group_id):
    group = Group.objects.get(id=group_id)
    form = CreateGroupForm(instance=group)
    if request.method == 'POST':
        form = CreateGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f"Group '{group.name}' updated successfully!")
            return redirect('group_list')
    return render(request, 'admin/create_group.html', {'form': form})

@user_passes_test(is_admin, login_url='no_permission')
def group_delete(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        group.delete()
        messages.success(request, f"Group '{group.name}' deleted successfully!")
        return redirect('group_list')
    messages.error(request, "Something went wrong")
    return redirect('group_list')

@user_passes_test(is_admin, login_url='no_permission')
def participant_list(request):
    participants = User.objects.all()
    return render(request, 'admin/participant_list.html', {
        'participants': participants
    })

@user_passes_test(is_admin, login_url='no_permission')
def delete_participant(request, user_id):
    participant = User.objects.get(id=user_id)
    if request.method == 'POST':
        participant.delete()
        messages.success(request, "Participant deleted successfully.")
        return redirect('participant_list')
    messages.error(request, "Something went wrong")
    return redirect('participant_list')