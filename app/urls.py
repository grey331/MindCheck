from django.urls import path
from app import views

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('contacts/', views.contacts, name='contacts'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Insights (Articles)
    path('insights/', views.insights, name='insights'),
    path('insights/create/', views.create_article, name='create_article'),
    path('insights/<int:article_id>/', views.view_article, name='view_article'),
    path('insights/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('insights/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('insights/<int:article_id>/like/', views.like_article, name='like_article'),
    
    # Chats
    path('chats/', views.chats, name='chats'),
    path('chats/<int:user_id>/', views.chat_detail, name='chat_detail'),
    
    # Consultations
    path('consultations/', views.consultations, name='consultations'),
    path('consultations/<int:psychologist_id>/', views.psychologist_detail, name='psychologist_detail'),
    path('consultations/<int:psychologist_id>/book/', views.book_consultation, name='book_consultation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/', views.view_appointment, name='view_appointment'),
    
    # Payments
    
    path('payment/<int:booking_id>/', views.payment_initiate, name='payment_initiate'),
    path('payment-status/<int:booking_id>/', views.payment_status, name='payment_status'),
    path('api/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
]
