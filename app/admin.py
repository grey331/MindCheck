from django.contrib import admin
from .models import UserProfile, Article, Message, Psychologist, Availability, Booking, Payment, Contact

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'author__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username')

@admin.register(Psychologist)
class PsychologistAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hourly_rate', 'rating', 'available')
    list_filter = ('available', 'specialization')
    search_fields = ('user__first_name', 'user__last_name', 'specialization')

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('psychologist', 'get_day_display', 'start_time', 'end_time')
    list_filter = ('day',)
    search_fields = ('psychologist__user__first_name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'psychologist', 'scheduled_date', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('user__username', 'psychologist__user__first_name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'mpesa_reference', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('mpesa_reference', 'phone_number', 'booking__id')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_replied', 'created_at')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject')
