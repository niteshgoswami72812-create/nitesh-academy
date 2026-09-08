import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlencode
import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Category, Course, Registration
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Home page
def home(request):
    top_courses = (
        Course.objects
        .select_related("category")
        .prefetch_related("topics")
        .order_by("price", "name")[:4]
    )

    data = {
        "featured_courses": top_courses,
        "course_count": Course.objects.count(),
    }

    return render(request, "home.html", data)


# Static pages
def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def help_page(request):
    return render(request, "help.html")


# All courses
def courses(request):
    categories = Category.objects.prefetch_related("courses").all()
    data = {
        "categories": categories,
        "course_count": Course.objects.count(),
    }
    return render(request, "courses.html", data)


# category ke hisaab se courses filter karna
def category_courses(request, category_id):
    cat = get_object_or_404(Category, id=category_id)
    search_keyword = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "")
    
    my_courses = cat.courses.prefetch_related("topics", "options").all()

    # Search wala logic
    if search_keyword:
        my_courses = my_courses.filter(Q(name__icontains=search_keyword))

    # Sorting ka logic
    if sort_by == "az":
        my_courses = my_courses.order_by("name")
    elif sort_by == "za":
        my_courses = my_courses.order_by("-name")
    elif sort_by == "price_low":
        my_courses = my_courses.order_by("price")
    elif sort_by == "price_high":
        my_courses = my_courses.order_by("-price")

    data = {
        "category": cat,
        "courses": my_courses,
        "search": search_keyword,
        "sort": sort_by,
    }
    return render(request, "category_courses.html", data)


# Course detail
def course_detail(request, course_id):
    query = Course.objects.select_related("category").prefetch_related("topics", "options")
    course = get_object_or_404(query, id=course_id)
    
    active_opts = course.options.filter(is_active=True)

    data = {
        "course": course,
        "course_options": active_opts,
    }
    return render(request, "course_detail.html", data)


# Safe next URL
def get_safe_next_url(request, default_url):
    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()

    if not next_url:
        return default_url

    is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )

    if is_safe:
        return next_url
    return default_url


# Registration
def registration(request):
    # agar pehle se login hai toh wapas bhej do
    if request.session.get("registration_user_id"):
        return redirect("courses")

    next_url = get_safe_next_url(request, reverse("courses"))

    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Form validation
        if not fullname:
            messages.error(request, "Please enter your full name.")
        elif not email:
            messages.error(request, "Please enter your email address.")
        elif not username:
            messages.error(request, "Please enter a username.")
        elif not password:
            messages.error(request, "Please enter a password.")
        elif not confirm_password:
            messages.error(request, "Please confirm your password.")
        elif password != confirm_password:
            messages.error(request, "Password and confirm password do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        elif Registration.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists. Please choose another username.")
        elif Registration.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists. Please use another email address.")
        else:
            # Save user
            try:
                with transaction.atomic():
                    Registration.objects.create(
                        fullname=fullname,
                        email=email,
                        username=username,
                        password=make_password(password), # password hash kar diya
                        confirm_password="",
                    )
            except IntegrityError:
                messages.error(request, "Username or email already exists.")
            else:
                messages.success(request, "Account created successfully. Please login.")
                
                # login page pe bhejna with next url
                login_url = reverse("login")
                query_string = urlencode({"next": next_url})
                return redirect(f"{login_url}?{query_string}")

    return render(request, "registration.html", {"next": next_url})


# Login
def login_view(request):
    if request.session.get("registration_user_id"):
        return redirect("courses")

    next_url = get_safe_next_url(request, reverse("courses"))

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username:
            messages.error(request, "Please enter your username.")
        elif not password:
            messages.error(request, "Please enter your password.")
        else:
            # user database se nikalo
            user = Registration.objects.filter(username__iexact=username).first()

            if user is None:
                messages.error(request, "User does not exist. Please create an account.")
            elif not check_password(password, user.password):
                messages.error(request, "Incorrect password. Please try again.")
            else:
                # login success hone pe session set karna
                request.session["registration_user_id"] = user.id
                request.session["registration_username"] = user.username
                request.session["registration_fullname"] = user.fullname
                request.session["registration_email"] = user.email
                
                request.session.set_expiry(60 * 60 * 24 * 7) # 7 din ke liye login

                messages.success(request, f"Welcome, {user.fullname}.")
                return redirect(next_url)

    return render(request, "login.html", {"next": next_url})


# Logout
def logout_view(request):
    request.session.flush() # saara session uda do
    messages.success(request, "You have logged out successfully.")
    return redirect("home")


# Checkout
def checkout(request):
    user_id = request.session.get("registration_user_id")

    if not user_id:
        messages.warning(request, "Please signup or login before checkout.")
        reg_url = reverse("registration")
        chk_url = reverse("checkout")
        query_string = urlencode({"next": chk_url})
        return redirect(f"{reg_url}?{query_string}")

    user = Registration.objects.filter(id=user_id).first()

    # agar user delete ho gaya ho database se
    if user is None:
        request.session.flush()
        messages.error(request, "Your account was not found. Please login again.")
        return redirect("login")

    return render(request, "checkout.html", {"registered_user": user})


# Razorpay payment
def payment_page(request):
    # order banayenge yaha
    if request.method != "POST":
        return redirect("checkout")

    if not request.session.get("registration_user_id"):
        messages.warning(request, "Please login before making a payment.")
        return redirect("login")

    total_value = request.POST.get("total", "0").strip()
    cart_data = request.POST.get("cart", "[]").strip()

    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        messages.error(request, "Cart information is invalid.")
        return redirect("checkout")

    if not isinstance(cart, list) or not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("checkout")

    try:
        # paise ko theek se format karna rounding ke sath
        final_price = Decimal(total_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        messages.error(request, "Invalid payment amount.")
        return redirect("checkout")

    if final_price <= 0:
        messages.error(request, "Cart total must be greater than zero.")
        return redirect("checkout")

    # razorpay sirf paise leta hai (rupees * 100)
    amount_paise = int((final_price * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    key_id = str(getattr(settings, "RAZORPAY_KEY_ID", "")).strip()
    key_secret = str(getattr(settings, "RAZORPAY_KEY_SECRET", "")).strip()

    if not key_id or not key_secret:
        messages.error(request, "Razorpay API keys are missing in settings.py.")
        return redirect("checkout")

    if not request.session.session_key:
        request.session.create()

    # Razorpay client
    client = razorpay.Client(auth=(key_id, key_secret))

    try:
        # Create Razorpay order
        payment = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"course_{request.session.session_key}"[:40],
            "notes": {
                "customer_id": str(request.session.get("registration_user_id", "")),
                "amount_rupees": str(final_price),
            },
        })
    except razorpay.errors.BadRequestError as error:
        print("Razorpay order error:", repr(error))
        messages.error(request, f"Unable to create payment order: {error}")
        return redirect("checkout")
    except Exception as error:
        print("Razorpay service error:", repr(error))
        messages.error(request, "Payment service is currently unavailable.")
        return redirect("checkout")

    # Save payment data in session
    request.session["razorpay_order_id"] = payment["id"]
    request.session["payment_total_rupees"] = str(final_price)
    request.session["payment_cart_json"] = json.dumps(cart)

    return render(request, "payment.html", {
        "payment": payment,
        "razorpay_key": key_id,
        "cart_json": json.dumps(cart),
        "display_total": final_price,
    })


# Payment success
def payment_success(request):
    # Verify payment signature
    if request.method != "POST":
        return redirect("courses")

    pay_id = request.POST.get("razorpay_payment_id", "").strip()
    ord_id = request.POST.get("razorpay_order_id", "").strip()
    sign = request.POST.get("razorpay_signature", "").strip()

    if not pay_id or not ord_id or not sign:
        messages.error(request, "Payment information is incomplete.")
        return redirect("checkout")

    # check karo session wala order id aur jo post se aya wo same hai ya nahi
    session_order_id = request.session.get("razorpay_order_id")
    if not session_order_id or ord_id != session_order_id:
        messages.error(request, "Payment order does not match this checkout.")
        return redirect("checkout")

    key_id = str(getattr(settings, "RAZORPAY_KEY_ID", "")).strip()
    key_secret = str(getattr(settings, "RAZORPAY_KEY_SECRET", "")).strip()

    if not key_id or not key_secret:
        messages.error(request, "Razorpay API keys are missing in settings.py.")
        return redirect("checkout")

    client = razorpay.Client(auth=(key_id, key_secret))

    # razorpay check karega ki payment ashi hai ya fake
    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": pay_id,
            "razorpay_order_id": ord_id,
            "razorpay_signature": sign,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed.")
        return redirect("checkout")
    except Exception as error:
        print("Razorpay verification error:", repr(error))
        messages.error(request, "Unable to verify payment.")
        return redirect("checkout")

    # jab sab sahi hai toh success page dikhao
    context = {
        "payment_id": pay_id,
        "order_id": ord_id,
        "display_total": request.session.get("payment_total_rupees", ""),
    }

    # Clear payment session data
    request.session.pop("razorpay_order_id", None)
    request.session.pop("payment_total_rupees", None)
    request.session.pop("payment_cart_json", None)

    return render(request, "payment_success.html", context)

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="Enrollment Successful - Nitesh Academy",
    message=f"""
Hello {student_name},

Your enrollment with Nitesh Academy has been successfully completed.

Name: {student_name}
Email: {student_email}
Course: {course_name}

Thank you for enrolling with Nitesh Academy.

Regards,
Nitesh Academy
""",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[student_email],
    fail_silently=False,
)