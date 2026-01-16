from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.views.generic import View, TemplateView, FormView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from events.models import Event, Category
from django.db.models import Count
from django.utils.timezone import now
from users.forms import CustomRegistrationForm, LoginForm, CreateGroupForm, EitProfileForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView

User = get_user_model()


# Mixins
class AdminRequiredMixin(UserPassesTestMixin):
    login_url = 'no_permission'
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class AdminOrganizerMixin(UserPassesTestMixin):
    login_url = 'no_permission'
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()


class AdminParticipantMixin(UserPassesTestMixin):
    login_url = 'no_permission'
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Participant']).exists()


# User Authentication
class SignUpView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('sign_in')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password1'))
        user.is_active = False
        user.save()
        group = Group.objects.get(name='Participant')
        user.groups.add(group)
        messages.success(self.request, "Registration successful. Please check your email to activate your account.")
        return super().form_valid(form)


class SignInView(FormView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, "Account is not active. Please check your email to activate your account.")
            return redirect('sign_in')
        login(self.request, user)
        return super().form_valid(form)


class SignOutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect('sign_in')


# Activate User
class ActivateUserView(View):
    def get(self, request, user_id, token):
        try:
            user = User.objects.get(id=user_id)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully!")
                return redirect('sign_in')
            return HttpResponse("Invalid token")
        except User.DoesNotExist:
            return HttpResponse("User does not exist")


# Dashboards
class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'admin/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.prefetch_related('groups')
        for user in users:
            user.role = user.groups.first().name if user.groups.exists() else "None"
        context.update({
            'total_users': User.objects.count(),
            'total_events': Event.objects.count(),
            'total_categories': Category.objects.count(),
            'total_rsvps': Event.objects.aggregate(total=Count('participants'))['total'],
            'users': users,
            'groups': Group.objects.all(),
        })
        return context


class OrganizerDashboardView(LoginRequiredMixin, AdminOrganizerMixin, TemplateView):
    template_name = 'admin/organizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(date__gte=now().date()).count()
        past_events = Event.objects.filter(date__lt=now().date()).count()
        total_participants = Event.objects.aggregate(total_participants=Count('participants'))['total_participants']
        today_events = Event.objects.filter(date=now().date()).select_related('category').prefetch_related('participants')

        event_filter = self.request.GET.get('filter', 'today')
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

        context.update({
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
            'total_participants': total_participants,
            'today_events': today_events,
            'filtered_events': filtered_events,
            'list_title': list_title,
        })
        return context


class ParticipantDashboardView(LoginRequiredMixin, AdminParticipantMixin, TemplateView):
    template_name = 'admin/participant.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.filter(date__gte=now().date()).select_related('category').order_by('date')
        context['events'] = events
        return context


# Role Assignment
class AssignRoleView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        role_id = request.POST.get('role_id')
        group = Group.objects.get(id=role_id)
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, f"{user.username} assigned to {group.name}")
        return redirect('dashboard')


# Group Management
class CreateGroupView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    template_name = 'admin/create_group.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('group_list')

    def form_valid(self, form):
        group = form.save()
        messages.success(self.request, f"Group '{group.name}' created successfully!")
        return super().form_valid(form)


class GroupListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Group
    template_name = 'admin/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.prefetch_related('permissions')


class GroupEditView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    template_name = 'admin/create_group.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('group_list')

    def get_initial(self):
        group = Group.objects.get(id=self.kwargs['group_id'])
        return {'name': group.name}

    def form_valid(self, form):
        group = Group.objects.get(id=self.kwargs['group_id'])
        group.name = form.cleaned_data['name']
        group.save()
        messages.success(self.request, f"Group '{group.name}' updated successfully!")
        return super().form_valid(form)


class GroupDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Group
    pk_url_kwarg = 'group_id'
    success_url = reverse_lazy('group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Group deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Participant Management
class ParticipantListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/participant_list.html'
    context_object_name = 'participants'


class DeleteParticipantView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    pk_url_kwarg = 'user_id'
    success_url = reverse_lazy('participant_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Participant deleted successfully.")
        return super().delete(request, *args, **kwargs)

# View Profile
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'user': user,
            'profile_picture': user.profile_picture,
            'name': f"{user.first_name} {user.last_name}" if user.first_name else user.username,
            'username': user.username,
            'email': user.email,
            'member_since': user.date_joined,
            'last_login': user.last_login,
            'phone_number': user.phone_number
        })
        return context


# Edit Profile
class EitProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EitProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profile updated successfully!")
        return redirect('profile')


# Change Password
class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)


# Password Reset - Email Sent
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


# Password Reset - Send Email
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign_in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        return context

    def form_valid(self, form):
        messages.success(self.request, "A reset email has been sent. Please check your email.")
        return super().form_valid(form)


# Password Reset Confirm - Set New Password
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign_in')

    def form_valid(self, form):
        messages.success(self.request, "Password reset successfully!")
        return super().form_valid(form)