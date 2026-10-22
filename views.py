from django.shortcuts import render,HttpResponse,redirect
from .models import Appointment,Admin
from django.contrib import messages
from django.core.mail import send_mail 
import random
from django.core.mail import EmailMultiAlternatives
from .models import SupportTickets
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.hashers import make_password,check_password
from datetime import datetime


def home(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        service = request.POST.get('service', '').strip()
        chiropractor = request.POST.get('chiropractor', '').strip()
        date = request.POST.get('date', '').strip()
        time = request.POST.get('time', '').strip()

        if not all([name, phone_number, service, chiropractor, date, time]):
            messages.error(request, 'Please fill in all appointment details.')
            return redirect('home')

        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time, '%H:%M').time()

        existing_appointments = Appointment.objects.filter(
            chiropractor=chiropractor,
            date=appointment_date
        )

        new_datetime = datetime.combine(
            appointment_date, appointment_time
        )

        for existing in existing_appointments:
            existing_datetime = datetime.combine(
                appointment_date, existing.time
            )

            difference = abs(
                (new_datetime - existing_datetime).total_seconds()
            ) / 60

            if difference < 20:
                messages.error(
                    request,
                    f'{chiropractor} has another appointment at '
                    f'{existing.time.strftime("%I:%M %p")}. '
                    'Please choose a time at least 20 minutes '
                    'before or after that appointment.'
                )
                return redirect('home')

        Appointment.objects.create(
            name=name,
            phone_number=phone_number,
            service=service,
            chiropractor=chiropractor,
            date=appointment_date,
            time=appointment_time
        )

        messages.success(
            request,
            'Your appointment has been booked successfully!'
        )

        return redirect('home')

    return render(request, 'home.html')


def base(request):
    return render(request,'base.html')


def about(request):
    return render(request,'about.html')


def adminLogin(request):
    show_otp = request.session.get('show_otp', False)
    email = request.session.get('temp_email', '')

    ADMIN_EMAIL = 'adityavikramsingh0004@gmail.com'
    ADMIN_PASSWORD = 'Aditya@123'

    if request.method == 'POST':

        user_otp = request.POST.get('otp')
        input_email = request.POST.get('username').lower()
        pwd = request.POST.get('password')

        # ============== OTP VERIFY ==============
        if user_otp:

            session_otp = request.session.get('otp')
            session_email = request.session.get('temp_email')

            if (
                session_email == ADMIN_EMAIL
                and user_otp == session_otp
            ):
                request.session['name'] = 'Aditya Vikram Singh'
                request.session['email'] = ADMIN_EMAIL


                request.session.set_expiry(0)

                request.session.pop('otp', None)
                request.session.pop('show_otp', None)
                request.session.pop('temp_email', None)

                messages.success(request, 'Login successful')
                return redirect('admin_panel')

            messages.error(request, 'Invalid OTP')
            return redirect('adminLogin')

        # ============== EMAIL & PASSWORD ==============
        if input_email != ADMIN_EMAIL:
            messages.error(request, 'Invalid admin email')
            return redirect('adminLogin')

        # ============== SEND OTP ==============
        otp = str(random.randint(100000, 999999))

        request.session['otp'] = otp
        request.session['temp_email'] = ADMIN_EMAIL
        request.session['show_otp'] = True
        request.session.set_expiry(300)

        try:
            send_mail(
                subject='Your Admin Login OTP',
                message=(
                    f'Your admin login OTP is {otp}. '
                    'It is valid for 5 minutes.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ADMIN_EMAIL],
                fail_silently=False
            )

            messages.success(
                request,
                'OTP sent to your email'
            )

        except Exception:
            request.session.pop('otp', None)
            request.session.pop('temp_email', None)
            request.session.pop('show_otp', None)

            messages.error(
                request,
                'OTP email could not be sent. Check email settings.'
            )

        return redirect('adminLogin')

    return render(
        request,
        'adminLogin.html',
        {
            'show_otp': show_otp,
            'email': email
        }
    )
    
def admin_panel(request):
    data = Appointment.objects.all()
    return render(request, 'admin_panel.html', {'data': data})
     
def LogOut(request):
    request.session.flush()
    return redirect('adminLogin')

def UserData(request):
    data = Appointment.objects.all()
    return render(request,'UserData.html',{'data':data})

def team(request):
    return render(request,'team.html')

def services(request):
    return render(request,'services.html')

def gallery(request):
    return render(request,'gallery.html')




def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if name and email and subject and message:

            # Save enquiry in database
            SupportTickets.objects.create(
                name=name,
                email=email,
                message=message
            )

            # Email template context
            context = {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            }

            # Load HTML email template
            html_content = render_to_string(
                "support.html",
                context
            )

            email_message = EmailMultiAlternatives(
                subject=f"Hospital Support: {subject}",
                body=(
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Subject: {subject}\n"
                    f"Message: {message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['shaktisingh90909090@gmail.com'],
                reply_to=[email],
            )

            email_message.attach_alternative(
                html_content,
                "text/html"
            )

            email_message.send(fail_silently=False)

            messages.success(
                    request,
                    "Your message has been sent successfully!"
                )

            return redirect("contact")

        messages.error(
            request,
            "Please fill in all fields."
        )

    return render(request, "contact.html")


def signUP(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signUP')

        hashed_password = make_password(password)

        user = Admin(name=name, email=email, password=hashed_password)
        user.save()

        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'signUP.html')

def signIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = Admin.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['photo'] = user.image.url if user.image else ''
            request.session.set_expiry(0)

            messages.success(request, 'Login successful')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'login.html')