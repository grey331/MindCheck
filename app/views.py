from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django_daraja.mpesa.core import MpesaClient
import json
from app.models import Article, Message, Psychologist, Booking, UserProfile, Availability, Payment, Contact
from app.forms import UserRegistrationForm, UserProfileForm, ArticleForm, MessageForm, BookingForm, ContactForm
import requests
import base64
from datetime import datetime
from django.conf import settings

# Home Page
def home(request):
    featured_articles = Article.objects.all()[:3]
    psychologists = Psychologist.objects.filter(available=True)[:6]
    context = {
        'featured_articles': featured_articles,
        'psychologists': psychologists,
    }
    return render(request, 'app/home.html', context)

# About Us
def about(request):
    return render(request, 'app/about.html')

# Pricing
def pricing(request):
    return render(request, 'app/pricing.html')

# Contacts
def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for contacting us. We will respond shortly.')
            return redirect('contacts')
    else:
        form = ContactForm()
    return render(request, 'app/contacts.html', {'form': form})

# Authentication
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'app/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

# Insights (Articles)
@login_required
def insights(request):
    articles = Article.objects.all()
    context = {'articles': articles}
    return render(request, 'app/insights.html', context)

@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article posted successfully!')
            return redirect('insights')
    else:
        form = ArticleForm()
    return render(request, 'app/create_article.html', {'form': form})
def view_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    context = {'article': article}
    return render(request, 'app/view_article.html', context)

@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.user:
        return HttpResponseForbidden("You can't edit this article")
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('insights')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'app/edit_article.html', {'form': form, 'article': article})

@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.user:
        return HttpResponseForbidden("You can't delete this article")
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
        return redirect('insights')
    return render(request, 'app/delete_article.html', {'article': article})

@login_required
@require_http_methods(["POST"])
def like_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user in article.likes.all():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': article.likes.count()})

# Chats
@login_required
def chats(request):
    conversations = Message.objects.filter(
        sender=request.user
    ).values_list('recipient', flat=True).distinct()
    
    context = {'conversations': conversations}
    return render(request, 'app/chats.html', context)

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = other_user
            message.save()
            return redirect('chat_detail', user_id=user_id)
    else:
        form = MessageForm()
    
    messages_list = Message.objects.filter(
        sender__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    ).order_by('created_at')
    
    Message.objects.filter(sender=other_user, recipient=request.user).update(is_read=True)
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'app/chat_detail.html', context)

# Consultation & Psychologist Booking
def consultations(request):
    psychologists = Psychologist.objects.filter(available=True)
    context = {'psychologists': psychologists}
    return render(request, 'app/consultations.html', context)

def psychologist_detail(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    availabilities = psychologist.availabilities.all()
    context = {
        'psychologist': psychologist,
        'availabilities': availabilities,
    }
    return render(request, 'app/psychologist_detail.html', context)

@login_required
def book_consultation(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            
            amount = psychologist.hourly_rate
            Payment.objects.create(
                booking=booking,
                amount=amount,
                phone_number=request.POST.get('phone_number'),
            )
            
            return redirect('payment_initiate', booking_id=booking.id)
    else:
        form = BookingForm(initial={'psychologist': psychologist})
    
    context = {
        'form': form,
        'psychologist': psychologist,
    }
    return render(request, 'app/book_consultation.html', context)

@login_required
def my_bookings(request):
    bookings = request.user.bookings.all()
    context = {'bookings': bookings}
    return render(request, 'app/my_bookings.html', context)
@login_required
def my_appointments (request):
    psychologist_profile = get_object_or_404(Psychologist, user=request.user)
    appointments = Booking.objects.filter(psychologist=psychologist_profile)
    context = {'appointments': appointments}
    return render(request, 'app/my_appointments.html', context)
@login_required
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Booking, id=appointment_id)
    context = {'appointment': appointment}
    return render(request, 'app/view_appointment.html', context)

# M-Pesa Payment Integration
@login_required
def payment_initiate(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = booking.payment
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = int(payment.amount)
        
        # Initialize M-Pesa client
        cl = MpesaClient()
        
        # Format phone number (from 07xxxxxxxx to 2547xxxxxxxx)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        account_reference = 'MindCheckBooking'  
        transaction_desc = 'Psychologist Consultation Booking'
        
        # Construct callback URL
        callback_url = 'https://api.darajambili.com/express-payment'
        
        # Initiate STK push
        response = cl.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            callback_url=callback_url
        )
        
        if response.response_code == "0":
            payment.mpesa_request_id = response.merchant_request_id
            payment.mpesa_checkout_id = response.checkout_request_id
            payment.status = 'pending'
            payment.save()
            
            messages.success(request, 'Payment request sent! Check your phone to complete payment.')
        else:
            messages.error(request, f'Failed to initiate payment: {response.error_message}')
        
        return redirect('payment_status', booking_id=booking_id)
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'app/payment_initiate.html', context)


# Add payment status view
@login_required
def payment_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = booking.payment
    
    context = {
        'booking': booking,
        'payment': payment,
    }
    return render(request, 'app/payment_status.html', context)

# M-Pesa Callback Handler

def mpesa_callback(request):
    try:
        data = request.body.decode('utf-8')
        callback_data = json.loads(data)
        
        result = callback_data.get('Body', {}).get('stkCallback', {})
        result_code = result.get('ResultCode')
        result_desc = result.get('ResultDesc')
        checkout_id = result.get('CheckoutRequestID')
        
        # Find payment by checkout ID
        try:
            payment = Payment.objects.get(mpesa_checkout_id=checkout_id)
            
            if result_code == 0:
                # Payment successful
                callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
                
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_reference = item.get('Value')
                    elif item.get('Name') == 'Amount':
                        payment.amount = item.get('Value')
                    elif item.get('Name') == 'PhoneNumber':
                        payment.phone_number = item.get('Value')
                
                payment.status = 'completed'
                payment.completed_at = datetime.now()
                payment.save()
                
                # Update booking status
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save()
                
                messages.success(request, 'Payment completed successfully!')
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, f'Payment failed: {result_desc}')
        
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'})
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
