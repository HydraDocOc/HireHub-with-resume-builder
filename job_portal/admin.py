from django.contrib import admin
from .models import CustomUser, Company, Job

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'mobile', 'role')
    search_fields = ('email', 'name')
    list_filter = ('role',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'posted_date')
    list_filter = ('job_type', 'company')
    search_fields = ('title', 'description', 'requirements')
    date_hierarchy = 'posted_date'
