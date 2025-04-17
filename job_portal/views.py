from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string

from .models import CustomUser, Company, Job
from .forms import UserRegisterForm, UserLoginForm, CompanyForm, JobForm, JobPostForm, SearchForm

class IndexView(ListView):
    model = Job
    template_name = 'jobs/index.html'
    context_object_name = 'jobs'
    ordering = ['-posted_date']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context
    
class CustomLoginView(LoginView):
    template_name = 'jobs/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # Check if the role matches
        user = form.get_user()
        if user.role != form.cleaned_data.get('role'):
            form.add_error(None, "Invalid role selection for this account.")
            return self.form_invalid(form)
        
        messages.success(self.request, "Login successful!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('job_portal:dashboard')

class RegisterView(FormView):
    template_name = 'jobs/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('job_portal:login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Registration successful! Please log in.")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Logged out successfully!")
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('job_portal:login')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/dashboard.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/profile.html'

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

class CompanyProfileView(DetailView):
    model = Company
    template_name = 'jobs/company_profile.html'
    context_object_name = 'company'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        return HttpResponseForbidden(render(self.request, 'jobs/error.html', {
            'error_code': 403,
            'error_message': 'Access Forbidden',
            'error_description': 'You do not have permission to access this resource.'
        }))

class PostJobView(AdminRequiredMixin, CreateView):
    model = Job
    form_class = JobPostForm
    template_name = 'jobs/post_job.html'
    success_url = reverse_lazy('job_portal:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        return context
        
    def form_valid(self, form):
        messages.success(self.request, "Job posted successfully!")
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                job = form.save()
                return JsonResponse({'message': 'Job posted successfully'})
            return JsonResponse({'errors': form.errors}, status=400)
        return super().post(request, *args, **kwargs)


class UpdateJobView(AdminRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/update_job.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        return context
        
    def get_success_url(self):
        messages.success(self.request, "Job updated successfully!")
        return reverse_lazy('job_portal:job_detail', kwargs={'pk': self.object.pk})

class DeleteJobView(AdminRequiredMixin, DeleteView):
    model = Job
    success_url = reverse_lazy('job_portal:index')
    
    def post(self, request, *args, **kwargs):
        messages.success(request, "Job deleted successfully!")
        return super().post(request, *args, **kwargs)

class SearchView(View):
    def get(self, request):
        keyword = request.GET.get('keyword', '').strip()
        location = request.GET.get('location', '').strip()
        
        # Start with base query
        query = Job.objects.all()
        
        # Apply filters if we have search terms
        if keyword:
            query = query.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(requirements__icontains=keyword) |
                Q(company__name__icontains=keyword)
            )
        
        if location:
            query = query.filter(location__icontains=location)
        
        # Execute query with ordering
        jobs = query.order_by('-posted_date')
        
        context = {
            'jobs': jobs,
            'search_keyword': keyword,
            'search_location': location
        }
        
        # If this is an AJAX request, return only the jobs list partial
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('jobs/_jobs_list.html', context, request=request)
            return JsonResponse({'html': html})
        
        # Otherwise return the full page
        return render(request, 'jobs/index.html', context)

class CompanyListView(AdminRequiredMixin, ListView):
    model = Company
    template_name = 'jobs/companies.html'
    context_object_name = 'companies'

class AddCompanyView(AdminRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'jobs/add_company.html'
    success_url = reverse_lazy('job_portal:list_companies')
    
    def form_valid(self, form):
        messages.success(self.request, "Company added successfully!")
        return super().form_valid(form)
