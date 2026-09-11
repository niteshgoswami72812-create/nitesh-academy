from .forms import (
    CategoryForm,
    CourseForm,
    TopicFormSet,
    CourseOptionFormSet,
    StudentProfileForm,
)
import json
import os
import base64
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlencode

import razorpay
import resend

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone

from .models import Category, Course, Registration, Payment, PaymentItem, StudentProfile, Enrollment

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
# =====================================================
# HOME PAGE
# =====================================================

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


# =====================================================
# STATIC PAGES
# =====================================================

def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def help_page(request):
    return render(request, "help.html")


# =====================================================
# COURSES
# =====================================================

def courses(request):
    categories = Category.objects.prefetch_related("courses").all()

    data = {
        "categories": categories,
        "course_count": Course.objects.count(),
    }

    return render(request, "courses.html", data)


def category_courses(request, category_id):
    cat = get_object_or_404(Category, id=category_id)

    search_keyword = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "")

    my_courses = cat.courses.prefetch_related(
        "topics",
        "options",
    ).all()

    if search_keyword:
        my_courses = my_courses.filter(
            Q(name__icontains=search_keyword)
        )

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

    return render(
        request,
        "category_courses.html",
        data,
    )


def course_detail(request, course_id):
    query = (
        Course.objects
        .select_related("category")
        .prefetch_related("topics", "options")
    )

    course = get_object_or_404(
        query,
        id=course_id,
    )

    active_opts = course.options.filter(
        is_active=True
    )

    data = {
        "course": course,
        "course_options": active_opts,
    }

    return render(
        request,
        "course_detail.html",
        data,
    )


# =====================================================
# SAFE REDIRECT
# =====================================================

def get_safe_next_url(request, default_url):
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or ""
    ).strip()

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


# =====================================================
# STUDENT REGISTRATION
# =====================================================

def registration(request):
    if request.session.get("registration_user_id"):
        return redirect("courses")

    next_url = get_safe_next_url(
        request,
        reverse("courses"),
    )

    if request.method == "POST":
        fullname = request.POST.get(
            "fullname",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        dob_value = request.POST.get(
            "dob",
            "",
        ).strip()

        try:
            dob = date.fromisoformat(dob_value) if dob_value else None
        except ValueError:
            dob = None

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        if not fullname:
            messages.error(
                request,
                "Please enter your full name.",
            )

        elif not email:
            messages.error(
                request,
                "Please enter your email address.",
            )

        elif not username:
            messages.error(
                request,
                "Please enter a username.",
            )

        elif not password:
            messages.error(
                request,
                "Please enter a password.",
            )

        elif not confirm_password:
            messages.error(
                request,
                "Please confirm your password.",
            )

        elif password != confirm_password:
            messages.error(
                request,
                "Password and confirm password do not match.",
            )

        elif len(password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters.",
            )

        elif Registration.objects.filter(
            username__iexact=username
        ).exists():
            messages.error(
                request,
                "Username already exists. Please choose another username.",
            )

        elif Registration.objects.filter(
            email__iexact=email
        ).exists():
            messages.error(
                request,
                "Email already exists. Please use another email address.",
            )

        else:
            try:
                with transaction.atomic():
                    Registration.objects.create(
                        fullname=fullname,
                        email=email,
                        dob=dob,
                        username=username,
                        password=make_password(password),
                        confirm_password="",
                    )

            except IntegrityError:
                messages.error(
                    request,
                    "Username or email already exists.",
                )

            else:
                messages.success(
                    request,
                    "Account created successfully. Please login.",
                )

                login_url = reverse("login")

                query_string = urlencode(
                    {
                        "next": next_url,
                    }
                )

                return redirect(
                    f"{login_url}?{query_string}"
                )

    return render(
        request,
        "registration.html",
        {
            "next": next_url,
        },
    )


# =====================================================
# STUDENT LOGIN
# =====================================================

def login_view(request):
    if request.session.get("registration_user_id"):
        return redirect("courses")

    next_url = get_safe_next_url(
        request,
        reverse("courses"),
    )

    if request.method == "POST":
        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        if not username:
            messages.error(
                request,
                "Please enter your username.",
            )

        elif not password:
            messages.error(
                request,
                "Please enter your password.",
            )

        else:
            user = Registration.objects.filter(
                username__iexact=username
            ).first()

            if user is None:
                messages.error(
                    request,
                    "User does not exist. Please create an account.",
                )

            elif not check_password(
                password,
                user.password,
            ):
                messages.error(
                    request,
                    "Incorrect password. Please try again.",
                )

            else:
                request.session[
                    "registration_user_id"
                ] = user.id

                request.session[
                    "registration_username"
                ] = user.username

                request.session[
                    "registration_fullname"
                ] = user.fullname

                request.session[
                    "registration_email"
                ] = user.email

                request.session.set_expiry(
                    60 * 60 * 24 * 7
                )

                messages.success(
                    request,
                    f"Welcome, {user.fullname}.",
                )

                return redirect(next_url)

    return render(
        request,
        "login.html",
        {
            "next": next_url,
        },
    )


# =====================================================
# STUDENT LOGOUT
# =====================================================

def logout_view(request):
    request.session.flush()

    messages.success(
        request,
        "You have logged out successfully.",
    )

    return redirect("home")



# =====================================================
# COURSE ENROLLMENT
# =====================================================

def start_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    request.session["pending_enrollment_course_id"] = course.id
    details_url = reverse("enrollment_details")

    if not request.session.get("registration_user_id"):
        registration_url = reverse("registration")
        query_string = urlencode({"next": details_url})
        return redirect(f"{registration_url}?{query_string}")

    return redirect("enrollment_details")


def enrollment_details(request):
    student_id = request.session.get("registration_user_id")
    course_id = request.session.get("pending_enrollment_course_id")

    if not student_id:
        login_url = reverse("login")
        query_string = urlencode({"next": reverse("enrollment_details")})
        return redirect(f"{login_url}?{query_string}")

    if not course_id:
        messages.warning(request, "Please select a course first.")
        return redirect("courses")

    student = Registration.objects.filter(id=student_id).first()
    if student is None:
        request.session.flush()
        return redirect("login")

    course = get_object_or_404(Course, id=course_id)
    profile = StudentProfile.objects.filter(student=student).first()

    initial = {}
    if profile is None:
        name_parts = student.fullname.split()
        initial = {
            "first_name": name_parts[0] if name_parts else "",
            "last_name": name_parts[-1] if len(name_parts) > 1 else "",
            "email": student.email,
            "dob": student.dob,
        }

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=profile, initial=initial)

        if form.is_valid():
            with transaction.atomic():
                profile = form.save(commit=False)
                profile.student = student
                profile.save()

                full_name = " ".join(
                    part for part in [
                        profile.first_name,
                        profile.middle_name,
                        profile.last_name,
                    ] if part
                )
                student.fullname = full_name
                student.email = profile.email
                student.dob = profile.dob
                student.save(update_fields=["fullname", "email", "dob"])

                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={"status": "registered"},
                )

            subject = f"Enrollment Successful - {course.name}"
            email_body = (
                f"Hello {full_name},\n\n"
                f"Your enrollment registration at NIT CODERS was successful.\n\n"
                f"Course: {course.name}\n"
                f"Duration: {course.duration}\n"
                f"Name: {full_name}\n"
                f"Email: {profile.email}\n"
                f"Mobile: {profile.phone}\n"
                f"Date of Birth: {profile.dob:%d-%m-%Y}\n"
                f"Current Study: {profile.current_study}\n"
                f"City: {profile.city}\n"
                f"Status: {enrollment.status.title()}\n\n"
                "Thank you,\nNIT CODERS"
            )

            email_sent = False
            try:
                resend.api_key = os.environ.get("RESEND_API_KEY", "").strip()
                if not resend.api_key:
                    raise RuntimeError("RESEND_API_KEY is not configured.")

                resend.Emails.send({
                    "from": os.environ.get(
                        "RESEND_FROM_EMAIL",
                        "NIT CODERS <onboarding@resend.dev>",
                    ).strip(),
                    "to": [profile.email],
                    "subject": subject,
                    "text": email_body,
                })
                email_sent = True
                print("Enrollment email sent via Resend to:", profile.email)
            except Exception as error:
                print("Enrollment email error:", repr(error))

            if email_sent and not enrollment.email_sent:
                enrollment.email_sent = True
                enrollment.save(update_fields=["email_sent"])

            request.session.pop("pending_enrollment_course_id", None)
            messages.success(request, "Your enrollment registration was completed successfully.")
            return redirect("enrollment_success", enrollment_id=enrollment.id)
    else:
        form = StudentProfileForm(instance=profile, initial=initial)

    return render(
        request,
        "enrollment_details.html",
        {
            "form": form,
            "course": course,
            "student": student,
        },
    )


def enrollment_success(request, enrollment_id):
    student_id = request.session.get("registration_user_id")
    if not student_id:
        return redirect("login")

    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        id=enrollment_id,
        student_id=student_id,
    )
    profile = StudentProfile.objects.filter(student_id=student_id).first()

    return render(
        request,
        "enrollment_success.html",
        {
            "enrollment": enrollment,
            "profile": profile,
        },
    )


# =====================================================
# CHECKOUT
# =====================================================

def checkout(request):
    user_id = request.session.get(
        "registration_user_id"
    )

    if not user_id:
        messages.warning(
            request,
            "Please signup or login before checkout.",
        )

        reg_url = reverse("registration")
        chk_url = reverse("checkout")

        query_string = urlencode(
            {
                "next": chk_url,
            }
        )

        return redirect(
            f"{reg_url}?{query_string}"
        )

    user = Registration.objects.filter(
        id=user_id
    ).first()

    if user is None:
        request.session.flush()

        messages.error(
            request,
            "Your account was not found. Please login again.",
        )

        return redirect("login")

    return render(
        request,
        "checkout.html",
        {
            "registered_user": user,
        },
    )


# =====================================================
# RAZORPAY CART VERIFICATION
# =====================================================

def _build_verified_cart(cart):
    verified_items = []
    total = Decimal("0.00")

    for item in cart:
        if not isinstance(item, dict):
            continue

        raw_course_id = (
            item.get("courseId")
            or str(
                item.get(
                    "id",
                    "",
                )
            ).split(":", 1)[0]
        )

        try:
            course_id = int(raw_course_id)

        except (TypeError, ValueError):
            continue

        try:
            quantity = int(
                item.get(
                    "quantity",
                    1,
                )
            )

        except (TypeError, ValueError):
            quantity = 1

        quantity = max(
            1,
            min(quantity, 20),
        )

        course = Course.objects.filter(
            id=course_id
        ).first()

        if course is None:
            continue

        selected_options = []
        option_total = 0

        raw_item_id = str(
            item.get(
                "id",
                "",
            )
        )

        if ":" in raw_item_id:
            option_key = raw_item_id.split(
                ":",
                1,
            )[1]

            if (
                option_key
                and option_key != "standard"
            ):
                option_ids = []

                for value in option_key.split("-"):
                    try:
                        option_ids.append(
                            int(value)
                        )

                    except ValueError:
                        pass

                options = course.options.filter(
                    id__in=option_ids,
                    is_active=True,
                )

                for option in options:
                    option_total += option.price_delta
                    selected_options.append(
                        option.name
                    )

        unit_price = max(
            0,
            course.price + option_total,
        )

        line_total = (
            Decimal(unit_price)
            * quantity
        )

        total += line_total

        display_name = course.name

        if selected_options:
            display_name += (
                f" ({', '.join(selected_options)})"
            )

        verified_items.append(
            {
                "id": raw_item_id or str(course.id),
                "courseId": str(course.id),
                "name": display_name,
                "price": unit_price,
                "quantity": quantity,
                "options": selected_options,
            }
        )

    return (
        verified_items,
        total.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        ),
    )


# =====================================================
# PAYMENT PAGE
# =====================================================

def payment_page(request):
    if request.method != "POST":
        return redirect("checkout")

    if not request.session.get(
        "registration_user_id"
    ):
        messages.warning(
            request,
            "Please login before making a payment.",
        )

        return redirect("login")

    cart_data = request.POST.get(
        "cart",
        "[]",
    ).strip()

    try:
        cart = json.loads(cart_data)

    except json.JSONDecodeError:
        messages.error(
            request,
            "Cart information is invalid.",
        )

        return redirect("checkout")

    if (
        not isinstance(cart, list)
        or not cart
    ):
        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("checkout")

    verified_cart, final_price = (
        _build_verified_cart(cart)
    )

    if (
        not verified_cart
        or final_price <= 0
    ):
        messages.error(
            request,
            "No valid courses were found in your cart.",
        )

        return redirect("checkout")

    amount_paise = int(
        final_price * 100
    )

    key_id = str(
        getattr(
            settings,
            "RAZORPAY_KEY_ID",
            "",
        )
    ).strip()

    key_secret = str(
        getattr(
            settings,
            "RAZORPAY_KEY_SECRET",
            "",
        )
    ).strip()

    if not key_id or not key_secret:
        messages.error(
            request,
            "Razorpay keys are not configured. "
            "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.",
        )

        return redirect("checkout")

    if not request.session.session_key:
        request.session.create()

    client = razorpay.Client(
        auth=(
            key_id,
            key_secret,
        )
    )

    try:
        payment = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": (
                    f"course_"
                    f"{request.session.session_key}"
                )[:40],
                "notes": {
                    "customer_id": str(
                        request.session.get(
                            "registration_user_id",
                            "",
                        )
                    ),
                    "amount_rupees": str(
                        final_price
                    ),
                },
            }
        )

    except razorpay.errors.BadRequestError as error:
        print(
            "Razorpay order error:",
            repr(error),
        )

        messages.error(
            request,
            "Unable to create payment order. "
            "Please verify your Razorpay keys and try again.",
        )

        return redirect("checkout")

    except Exception as error:
        print(
            "Razorpay service error:",
            repr(error),
        )

        messages.error(
            request,
            "Payment service is currently unavailable.",
        )

        return redirect("checkout")

    request.session[
        "razorpay_order_id"
    ] = payment["id"]

    request.session[
        "payment_total_rupees"
    ] = str(final_price)

    request.session[
        "payment_cart_json"
    ] = json.dumps(
        verified_cart
    )

    return render(
        request,
        "payment.html",
        {
            "payment": payment,
            "razorpay_key": key_id,
            "cart_json": json.dumps(
                verified_cart
            ),
            "display_total": final_price,
        },
    )


# =====================================================
# PAYMENT SUCCESS
# =====================================================

def payment_success(request):
    if request.method != "POST":
        return redirect("courses")

    pay_id = request.POST.get("razorpay_payment_id", "").strip()
    ord_id = request.POST.get("razorpay_order_id", "").strip()
    sign = request.POST.get("razorpay_signature", "").strip()

    if not pay_id or not ord_id or not sign:
        messages.error(request, "Payment information is incomplete.")
        return redirect("checkout")

    session_order_id = request.session.get("razorpay_order_id")
    if not session_order_id or ord_id != session_order_id:
        messages.error(request, "Payment order does not match this checkout.")
        return redirect("checkout")

    key_id = str(getattr(settings, "RAZORPAY_KEY_ID", "")).strip()
    key_secret = str(getattr(settings, "RAZORPAY_KEY_SECRET", "")).strip()

    if not key_id or not key_secret:
        messages.error(request, "Razorpay keys are not configured.")
        return redirect("checkout")

    client = razorpay.Client(auth=(key_id, key_secret))

    try:
        client.utility.verify_payment_signature({
            "razorpay_payment_id": pay_id,
            "razorpay_order_id": ord_id,
            "razorpay_signature": sign,
        })
        payment_data = client.payment.fetch(pay_id)
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed.")
        return redirect("checkout")
    except Exception as error:
        print("Razorpay verification error:", repr(error))
        messages.error(request, "Unable to verify payment.")
        return redirect("checkout")

    expected_total = Decimal(
        str(request.session.get("payment_total_rupees", "0"))
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    fetched_amount = Decimal(str(payment_data.get("amount", 0))) / Decimal("100")
    fetched_order_id = str(payment_data.get("order_id", ""))

    if fetched_order_id != ord_id or fetched_amount != expected_total:
        messages.error(request, "Payment amount or order verification failed.")
        return redirect("checkout")

    try:
        cart = json.loads(request.session.get("payment_cart_json", "[]"))
    except json.JSONDecodeError:
        cart = []

    student = Registration.objects.filter(
        id=request.session.get("registration_user_id")
    ).first()

    method = str(payment_data.get("method") or "").strip()
    bank = str(payment_data.get("bank") or "").strip()
    wallet = str(payment_data.get("wallet") or "").strip()
    vpa = str(payment_data.get("vpa") or "").strip()
    status = str(payment_data.get("status") or "paid").strip()
    currency = str(payment_data.get("currency") or "INR").strip()

    card = payment_data.get("card") or {}
    card_last4 = str(card.get("last4") or "").strip()
    card_network = str(card.get("network") or "").strip()

    paid_timestamp = payment_data.get("created_at")
    if paid_timestamp:
        paid_at = datetime.fromtimestamp(
            paid_timestamp,
            tz=timezone.get_current_timezone(),
        )
    else:
        paid_at = timezone.now()

    receipt_number = f"NA-{timezone.now():%Y%m%d}-{pay_id[-8:].upper()}"

    with transaction.atomic():
        payment_record, created = Payment.objects.get_or_create(
            razorpay_payment_id=pay_id,
            defaults={
                "student": student,
                "receipt_number": receipt_number,
                "razorpay_order_id": ord_id,
                "amount": expected_total,
                "currency": currency,
                "status": status,
                "method": method,
                "bank": bank,
                "wallet": wallet,
                "vpa": vpa,
                "card_last4": card_last4,
                "card_network": card_network,
                "paid_at": paid_at,
            },
        )

        if created:
            for item in cart:
                try:
                    course_id = int(item.get("courseId"))
                except (TypeError, ValueError):
                    course_id = None

                course = Course.objects.filter(id=course_id).first()
                quantity = max(1, int(item.get("quantity", 1)))
                unit_price = Decimal(str(item.get("price", 0))).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

                PaymentItem.objects.create(
                    payment=payment_record,
                    course=course,
                    course_name=str(item.get("name") or (course.name if course else "Course")),
                    options=", ".join(item.get("options") or []),
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=(unit_price * quantity).quantize(Decimal("0.01")),
                )

    # Payment verify hone ke baad receipt student ke enrollment/profile email par bhejo
    receipt_email = ""
    student_profile = None

    if student:
        student_profile = StudentProfile.objects.filter(student=student).first()

        if student_profile and student_profile.email:
            receipt_email = student_profile.email.strip()
        elif student.email:
            receipt_email = student.email.strip()

    if receipt_email and created:
        receipt_context = {
            "receipt": payment_record,
            "student": student,
            "profile": student_profile,
        }

        html_message = render_to_string(
            "emails/payment_receipt.html",
            receipt_context,
        )

        item_lines = []
        for item in payment_record.items.all():
            item_lines.append(
                f"{item.course_name} - Qty: {item.quantity} - Rs. {item.line_total}"
            )

        plain_items = "\n".join(item_lines) or "Course details available in your receipt."

        plain_message = (
            f"Hello {student.fullname if student else 'Student'},\n\n"
            "Your payment has been successfully received by NIT CODERS.\n\n"
            f"Receipt No: {payment_record.receipt_number}\n"
            f"Payment ID: {payment_record.razorpay_payment_id}\n"
            f"Order ID: {payment_record.razorpay_order_id}\n"
            f"Amount Paid: Rs. {payment_record.amount}\n"
            f"Payment Method: {payment_record.method or 'Online'}\n\n"
            f"Courses:\n{plain_items}\n\n"
            "Thank you for choosing NIT CODERS."
        )

        # Professional dark-theme PDF receipt attachment
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
        page_width, page_height = A4
        pdf.setTitle(f"Payment Receipt - {payment_record.receipt_number}")

        navy = colors.HexColor("#070B12")
        surface = colors.HexColor("#0C1424")
        surface_2 = colors.HexColor("#111C30")
        blue = colors.HexColor("#3B82F6")
        purple = colors.HexColor("#7C3AED")
        green = colors.HexColor("#22C55E")
        white = colors.HexColor("#F8FAFC")
        muted = colors.HexColor("#94A3B8")
        border = colors.HexColor("#26364F")

        margin = 34
        content_width = page_width - (margin * 2)

        def rounded_box(x, y, w, h, fill, stroke=border, radius=12):
            pdf.setFillColor(fill)
            pdf.setStrokeColor(stroke)
            pdf.roundRect(x, y, w, h, radius, fill=1, stroke=1)

        def draw_label_value(label, value, x, y, value_x=None, max_chars=52):
            value = str(value or "-")
            if len(value) > max_chars:
                value = value[:max_chars - 3] + "..."
            pdf.setFillColor(muted)
            pdf.setFont("Helvetica", 8.5)
            pdf.drawString(x, y, label.upper())
            pdf.setFillColor(white)
            pdf.setFont("Helvetica-Bold", 9.5)
            pdf.drawString(value_x or (x + 92), y, value)

        def wrap_text(value, font_name, font_size, max_width):
            words = str(value or "").split()
            lines = []
            current = ""
            for word in words:
                trial = word if not current else current + " " + word
                if stringWidth(trial, font_name, font_size) <= max_width:
                    current = trial
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            return lines or ["-"]

        # Full dark background
        pdf.setFillColor(navy)
        pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

        # Premium header card
        header_h = 112
        header_y = page_height - margin - header_h
        rounded_box(margin, header_y, content_width, header_h, surface, blue, 16)

        # Accent bars
        pdf.setFillColor(blue)
        pdf.roundRect(margin, header_y + header_h - 7, content_width * 0.62, 7, 4, fill=1, stroke=0)
        pdf.setFillColor(purple)
        pdf.roundRect(margin + content_width * 0.58, header_y + header_h - 7, content_width * 0.42, 7, 4, fill=1, stroke=0)

        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(margin + 22, header_y + 70, "NIT CODERS")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin + 22, header_y + 50, "OFFICIAL PAYMENT RECEIPT")

        badge_w = 138
        badge_h = 28
        badge_x = margin + content_width - badge_w - 20
        badge_y = header_y + 57
        pdf.setFillColor(colors.HexColor("#0B2B1B"))
        pdf.setStrokeColor(green)
        pdf.roundRect(badge_x, badge_y, badge_w, badge_h, 14, fill=1, stroke=1)
        pdf.setFillColor(green)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawCentredString(badge_x + badge_w / 2, badge_y + 9, "PAYMENT SUCCESSFUL")

        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(margin + content_width - 20, header_y + 28, "RECEIPT NO.")
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawRightString(
            margin + content_width - 20,
            header_y + 15,
            payment_record.receipt_number,
        )

        if student_profile:
            student_name = " ".join(
                part for part in [
                    student_profile.first_name,
                    student_profile.middle_name,
                    student_profile.last_name,
                ] if part
            )
        elif student:
            student_name = student.fullname
        else:
            student_name = "Student"

        # Student + payment detail cards
        cards_top = header_y - 18
        gap = 12
        card_w = (content_width - gap) / 2
        card_h = 154
        card_y = cards_top - card_h

        rounded_box(margin, card_y, card_w, card_h, surface_2)
        rounded_box(margin + card_w + gap, card_y, card_w, card_h, surface_2)

        pdf.setFillColor(blue)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margin + 16, card_y + card_h - 24, "STUDENT DETAILS")

        left_x = margin + 16
        ly = card_y + card_h - 48
        draw_label_value("Name", student_name, left_x, ly, left_x + 62, 34)
        ly -= 22
        draw_label_value("Email", receipt_email, left_x, ly, left_x + 62, 34)
        if student_profile:
            ly -= 22
            draw_label_value("Mobile", student_profile.phone, left_x, ly, left_x + 62, 24)
            ly -= 22
            dob_text = student_profile.dob.strftime("%d %b %Y") if student_profile.dob else "-"
            draw_label_value("DOB", dob_text, left_x, ly, left_x + 62, 24)
            ly -= 22
            draw_label_value("City", student_profile.city, left_x, ly, left_x + 62, 24)

        right_x = margin + card_w + gap + 16
        pdf.setFillColor(purple)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(right_x, card_y + card_h - 24, "PAYMENT DETAILS")

        ry = card_y + card_h - 48
        draw_label_value("Payment ID", payment_record.razorpay_payment_id, right_x, ry, right_x + 76, 30)
        ry -= 22
        draw_label_value("Order ID", payment_record.razorpay_order_id, right_x, ry, right_x + 76, 30)
        ry -= 22
        draw_label_value("Method", (payment_record.method or "Online").title(), right_x, ry, right_x + 76, 22)

        method_extra = payment_record.bank or payment_record.wallet or payment_record.vpa
        if payment_record.card_last4:
            method_extra = f"{payment_record.card_network or 'Card'} •••• {payment_record.card_last4}"
        ry -= 22
        draw_label_value("Provider", method_extra or "-", right_x, ry, right_x + 76, 26)
        ry -= 22
        paid_text = payment_record.paid_at.strftime("%d %b %Y, %I:%M %p")
        draw_label_value("Paid On", paid_text, right_x, ry, right_x + 76, 26)

        # Course table
        table_top = card_y - 18
        table_h = 190
        table_y = table_top - table_h
        rounded_box(margin, table_y, content_width, table_h, surface)

        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margin + 16, table_y + table_h - 25, "COURSE DETAILS")

        header_row_y = table_y + table_h - 52
        pdf.setFillColor(surface_2)
        pdf.roundRect(margin + 14, header_row_y - 8, content_width - 28, 27, 7, fill=1, stroke=0)

        col_course = margin + 25
        col_qty = margin + content_width - 205
        col_price = margin + content_width - 145
        col_total = margin + content_width - 72

        pdf.setFillColor(muted)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(col_course, header_row_y, "COURSE / OPTIONS")
        pdf.drawCentredString(col_qty, header_row_y, "QTY")
        pdf.drawRightString(col_price, header_row_y, "UNIT PRICE")
        pdf.drawRightString(margin + content_width - 24, header_row_y, "TOTAL")

        row_y = header_row_y - 28
        for item in payment_record.items.all():
            course_lines = wrap_text(item.course_name, "Helvetica-Bold", 9, 250)
            option_lines = wrap_text(item.options, "Helvetica", 7.5, 250) if item.options else []
            needed = (len(course_lines) * 12) + (len(option_lines) * 10) + 8

            if row_y - needed < table_y + 20:
                break

            pdf.setFillColor(white)
            pdf.setFont("Helvetica-Bold", 9)
            line_y = row_y
            for line in course_lines:
                pdf.drawString(col_course, line_y, line)
                line_y -= 12

            if option_lines:
                pdf.setFillColor(muted)
                pdf.setFont("Helvetica", 7.5)
                for line in option_lines:
                    pdf.drawString(col_course, line_y, line)
                    line_y -= 10

            pdf.setFillColor(white)
            pdf.setFont("Helvetica", 9)
            pdf.drawCentredString(col_qty, row_y, str(item.quantity))
            pdf.drawRightString(col_price, row_y, f"Rs. {item.unit_price}")
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawRightString(margin + content_width - 24, row_y, f"Rs. {item.line_total}")

            row_y -= max(needed, 34)
            pdf.setStrokeColor(border)
            pdf.line(margin + 20, row_y + 8, margin + content_width - 20, row_y + 8)

        # Total card
        total_h = 74
        total_y = table_y - total_h - 16
        rounded_box(margin, total_y, content_width, total_h, surface_2, blue, 14)

        pdf.setFillColor(muted)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(margin + 20, total_y + 43, "PAYMENT STATUS")
        pdf.setFillColor(green)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margin + 20, total_y + 23, "CAPTURED / PAID")

        pdf.setFillColor(muted)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawRightString(margin + content_width - 20, total_y + 45, "TOTAL PAID")
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawRightString(
            margin + content_width - 20,
            total_y + 20,
            f"Rs. {payment_record.amount}",
        )

        # Footer
        footer_y = 42
        pdf.setStrokeColor(border)
        pdf.line(margin, footer_y + 26, margin + content_width, footer_y + 26)
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(margin, footer_y + 8, "Thank you for choosing NIT CODERS.")
        pdf.drawRightString(
            margin + content_width,
            footer_y + 8,
            "Computer-generated payment receipt",
        )

        pdf.save()
        pdf_buffer.seek(0)

        pdf_bytes = pdf_buffer.read()

        try:
            resend.api_key = os.environ.get("RESEND_API_KEY", "").strip()
            if not resend.api_key:
                raise RuntimeError("RESEND_API_KEY is not configured.")

            resend.Emails.send({
                "from": os.environ.get(
                    "RESEND_FROM_EMAIL",
                    "NIT CODERS<onboarding@resend.dev>",
                ).strip(),
                "to": [receipt_email],
                "subject": f"Payment Receipt - {payment_record.receipt_number}",
                "text": plain_message,
                "html": html_message,
                "attachments": [
                    {
                        "filename": f"{payment_record.receipt_number}.pdf",
                        "content": base64.b64encode(pdf_bytes).decode("ascii"),
                    }
                ],
            })
            print("Payment receipt email sent via Resend to:", receipt_email)
        except Exception as error:
            print("Payment receipt email error:", repr(error))

    request.session.pop("razorpay_order_id", None)
    request.session.pop("payment_total_rupees", None)
    request.session.pop("payment_cart_json", None)

    return render(
        request,
        "payment_success.html",
        {"receipt": payment_record},
    )


def payment_receipt(request, receipt_number):
    receipt = get_object_or_404(
        Payment.objects.select_related("student").prefetch_related("items"),
        receipt_number=receipt_number,
    )

    student_id = request.session.get("registration_user_id")
    is_owner = receipt.student_id and receipt.student_id == student_id
    is_admin = request.user.is_authenticated and request.user.is_staff

    if not is_owner and not is_admin:
        messages.error(request, "You are not allowed to view this receipt.")
        return redirect("home")

    return render(request, "payment_success.html", {"receipt": receipt})


# =====================================================
# CUSTOM ADMIN PANEL
# =====================================================

def admin_check(user):
    return (
        user.is_authenticated
        and user.is_staff
    )


def dashboard_login(request):
    if (
        request.user.is_authenticated
        and request.user.is_staff
    ):
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        if not username:
            messages.error(
                request,
                "Please enter your username.",
            )

        elif not password:
            messages.error(
                request,
                "Please enter your password.",
            )

        else:
            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is None:
                messages.error(
                    request,
                    "Invalid username or password.",
                )

            elif not user.is_staff:
                messages.error(
                    request,
                    "You do not have permission to access the admin dashboard.",
                )

            else:
                auth_login(
                    request,
                    user,
                )

                messages.success(
                    request,
                    "Admin login successful.",
                )

                return redirect("dashboard")

    return render(
        request,
        "dashboard/login.html",
    )


@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard(request):

    recent_students = Registration.objects.order_by("-id")[:5]
    recent_courses = Course.objects.select_related("category").order_by("-id")[:5]

    context = {
        "admin_user": request.user,
        "total_students": Registration.objects.count(),
        "total_courses": Course.objects.count(),
        "total_categories": Category.objects.count(),
        "recent_students": recent_students,
        "recent_courses": recent_courses,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )


def dashboard_logout(request):
    auth_logout(request)

    messages.success(
        request,
        "Admin logged out successfully.",
    )

    return redirect(
        "dashboard_login"
    )

# =====================================================
# CUSTOM ADMIN - COURSE MANAGEMENT
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_courses(request):

    course_list = (
        Course.objects
        .select_related("category")
        .prefetch_related("topics", "options")
        .order_by("-id")
    )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:
        course_list = course_list.filter(
            Q(name__icontains=search)
            | Q(category__name__icontains=search)
        )

    context = {
        "courses": course_list,
        "search": search,
    }

    return render(
        request,
        "dashboard/courses.html",
        context,
    )


# =====================================================
# ADD COURSE
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_course_add(request):

    if request.method == "POST":

        form = CourseForm(
            request.POST,
        )

        if form.is_valid():

            with transaction.atomic():

                course = form.save()

                topic_formset = TopicFormSet(
                    request.POST,
                    instance=course,
                    prefix="topics",
                )

                option_formset = CourseOptionFormSet(
                    request.POST,
                    instance=course,
                    prefix="options",
                )

                if (
                    topic_formset.is_valid()
                    and option_formset.is_valid()
                ):

                    topic_formset.save()
                    option_formset.save()

                    messages.success(
                        request,
                        "Course added successfully.",
                    )

                    return redirect(
                        "dashboard_courses"
                    )

                course.delete()

        else:
            topic_formset = TopicFormSet(
                request.POST,
                prefix="topics",
            )

            option_formset = CourseOptionFormSet(
                request.POST,
                prefix="options",
            )

    else:

        form = CourseForm()

        topic_formset = TopicFormSet(
            prefix="topics",
        )

        option_formset = CourseOptionFormSet(
            prefix="options",
        )

    context = {
        "form": form,
        "topic_formset": topic_formset,
        "option_formset": option_formset,
        "page_title": "Add New Course",
        "button_text": "Create Course",
    }

    return render(
        request,
        "dashboard/course_form.html",
        context,
    )


# =====================================================
# EDIT COURSE
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_course_edit(
    request,
    course_id,
):

    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course,
        )

        topic_formset = TopicFormSet(
            request.POST,
            instance=course,
            prefix="topics",
        )

        option_formset = CourseOptionFormSet(
            request.POST,
            instance=course,
            prefix="options",
        )

        if (
            form.is_valid()
            and topic_formset.is_valid()
            and option_formset.is_valid()
        ):

            with transaction.atomic():

                form.save()
                topic_formset.save()
                option_formset.save()

            messages.success(
                request,
                "Course updated successfully.",
            )

            return redirect(
                "dashboard_courses"
            )

    else:

        form = CourseForm(
            instance=course,
        )

        topic_formset = TopicFormSet(
            instance=course,
            prefix="topics",
        )

        option_formset = CourseOptionFormSet(
            instance=course,
            prefix="options",
        )

    context = {
        "form": form,
        "topic_formset": topic_formset,
        "option_formset": option_formset,
        "course": course,
        "page_title": "Edit Course",
        "button_text": "Update Course",
    }

    return render(
        request,
        "dashboard/course_form.html",
        context,
    )


# =====================================================
# DELETE COURSE
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_course_delete(
    request,
    course_id,
):

    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if request.method == "POST":

        course_name = course.name

        course.delete()

        messages.success(
            request,
            f"{course_name} deleted successfully.",
        )

    return redirect(
        "dashboard_courses"
    )


# =====================================================
# CATEGORY MANAGEMENT
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_categories(request):

    categories = (
        Category.objects
        .prefetch_related("courses")
        .order_by("name")
    )

    context = {
        "categories": categories,
    }

    return render(
        request,
        "dashboard/categories.html",
        context,
    )


# =====================================================
# ADD CATEGORY
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_category_add(request):

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category added successfully.",
            )

            return redirect(
                "dashboard_categories"
            )

    else:

        form = CategoryForm()

    return render(
        request,
        "dashboard/category_form.html",
        {
            "form": form,
            "page_title": "Add Category",
            "button_text": "Create Category",
        },
    )


# =====================================================
# EDIT CATEGORY
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_category_edit(
    request,
    category_id,
):

    category = get_object_or_404(
        Category,
        id=category_id,
    )

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            instance=category,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category updated successfully.",
            )

            return redirect(
                "dashboard_categories"
            )

    else:

        form = CategoryForm(
            instance=category,
        )

    return render(
        request,
        "dashboard/category_form.html",
        {
            "form": form,
            "category": category,
            "page_title": "Edit Category",
            "button_text": "Update Category",
        },
    )


# =====================================================
# DELETE CATEGORY
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_category_delete(
    request,
    category_id,
):

    category = get_object_or_404(
        Category,
        id=category_id,
    )

    if request.method == "POST":

        if category.courses.exists():

            messages.error(
                request,
                "This category contains courses. "
                "Move or delete those courses first.",
            )

        else:

            category.delete()

            messages.success(
                request,
                "Category deleted successfully.",
            )

    return redirect(
        "dashboard_categories"
    )


# =====================================================
# STUDENT MANAGEMENT
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_students(request):

    students = Registration.objects.order_by(
        "-created_at"
    )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:

        students = students.filter(
            Q(fullname__icontains=search)
            | Q(username__icontains=search)
            | Q(email__icontains=search)
        )

    context = {
        "students": students,
        "search": search,
    }

    return render(
        request,
        "dashboard/students.html",
        context,
    )


# =====================================================
# DELETE STUDENT
# =====================================================

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_student_delete(
    request,
    student_id,
):

    student = get_object_or_404(
        Registration,
        id=student_id,
    )

    if request.method == "POST":

        student_name = student.fullname

        student.delete()

        messages.success(
            request,
            f"{student_name} deleted successfully.",
        )

    return redirect(
        "dashboard_students"
    )

@user_passes_test(admin_check, login_url="dashboard_login")

@user_passes_test(
    admin_check,
    login_url="dashboard_login",
)
def dashboard_enrollments(request):
    search = request.GET.get("search", "").strip()
    enrollments = Enrollment.objects.select_related(
        "student",
        "course",
    ).order_by("-created_at")

    if search:
        enrollments = enrollments.filter(
            Q(student__fullname__icontains=search)
            | Q(student__email__icontains=search)
            | Q(course__name__icontains=search)
        )

    return render(
        request,
        "dashboard/enrollments.html",
        {
            "enrollments": enrollments,
            "search": search,
        },
    )

def dashboard_payments(request):
    payments = Payment.objects.select_related("student").prefetch_related("items")
    search = request.GET.get("search", "").strip()

    if search:
        payments = payments.filter(
            Q(receipt_number__icontains=search)
            | Q(razorpay_payment_id__icontains=search)
            | Q(student__fullname__icontains=search)
            | Q(student__email__icontains=search)
        )

    return render(
        request,
        "dashboard/payments.html",
        {"payments": payments, "search": search},
    )
