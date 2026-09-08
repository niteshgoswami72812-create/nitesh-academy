import os

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path

from myapp import views


def create_admin_temp(request):
    token = request.GET.get("token", "")
    expected_token = os.environ.get("TEMP_ADMIN_TOKEN", "").strip()

    if not expected_token or token != expected_token:
        return HttpResponse("Unauthorized", status=403)

    username = os.environ.get("TEMP_ADMIN_USERNAME", "").strip()
    password = os.environ.get("TEMP_ADMIN_PASSWORD", "").strip()
    email = os.environ.get("TEMP_ADMIN_EMAIL", "").strip()

    if not username or not password:
        return HttpResponse(
            "TEMP_ADMIN_USERNAME or TEMP_ADMIN_PASSWORD is missing.",
            status=500,
        )

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
        },
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()

    if created:
        return HttpResponse("Admin created successfully.")

    return HttpResponse("Admin password reset successfully.")


urlpatterns = [

    # ==========================================
    # DJANGO DEFAULT ADMIN
    # ==========================================

    path(
        "admin/",
        admin.site.urls,
    ),

    # ==========================================
    # TEMP ADMIN CREATION
    # Delete this route after admin is created
    # ==========================================

    path(
        "create-admin-temp/",
        create_admin_temp,
        name="create_admin_temp",
    ),

    # ==========================================
    # CUSTOM ADMIN DASHBOARD
    # ==========================================

    path(
        "dashboard/login/",
        views.dashboard_login,
        name="dashboard_login",
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "dashboard/logout/",
        views.dashboard_logout,
        name="dashboard_logout",
    ),

    # ==========================================
    # DASHBOARD - COURSES
    # ==========================================

    path(
        "dashboard/courses/",
        views.dashboard_courses,
        name="dashboard_courses",
    ),

    path(
        "dashboard/courses/add/",
        views.dashboard_course_add,
        name="dashboard_course_add",
    ),

    path(
        "dashboard/courses/<int:course_id>/edit/",
        views.dashboard_course_edit,
        name="dashboard_course_edit",
    ),

    path(
        "dashboard/courses/<int:course_id>/delete/",
        views.dashboard_course_delete,
        name="dashboard_course_delete",
    ),

    # ==========================================
    # DASHBOARD - CATEGORIES
    # ==========================================

    path(
        "dashboard/categories/",
        views.dashboard_categories,
        name="dashboard_categories",
    ),

    path(
        "dashboard/categories/add/",
        views.dashboard_category_add,
        name="dashboard_category_add",
    ),

    path(
        "dashboard/categories/<int:category_id>/edit/",
        views.dashboard_category_edit,
        name="dashboard_category_edit",
    ),

    path(
        "dashboard/categories/<int:category_id>/delete/",
        views.dashboard_category_delete,
        name="dashboard_category_delete",
    ),

    # ==========================================
    # DASHBOARD - STUDENTS
    # ==========================================

    path(
        "dashboard/students/",
        views.dashboard_students,
        name="dashboard_students",
    ),

    path(
        "dashboard/students/<int:student_id>/delete/",
        views.dashboard_student_delete,
        name="dashboard_student_delete",
    ),

    # ==========================================
    # DASHBOARD - ENROLLMENTS
    # ==========================================

    path(
        "dashboard/enrollments/",
        views.dashboard_enrollments,
        name="dashboard_enrollments",
    ),

    # ==========================================
    # DASHBOARD - PAYMENTS
    # ==========================================

    path(
        "dashboard/payments/",
        views.dashboard_payments,
        name="dashboard_payments",
    ),

    # ==========================================
    # WEBSITE
    # ==========================================

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "about/",
        views.about,
        name="about",
    ),

    path(
        "contact/",
        views.contact,
        name="contact",
    ),

    path(
        "help/",
        views.help_page,
        name="help",
    ),

    # ==========================================
    # COURSES
    # ==========================================

    path(
        "courses/",
        views.courses,
        name="courses",
    ),

    path(
        "courses/category/<int:category_id>/",
        views.category_courses,
        name="category_courses",
    ),

    path(
        "courses/course/<int:course_id>/",
        views.course_detail,
        name="course_detail",
    ),

    # ==========================================
    # STUDENT AUTHENTICATION
    # ==========================================

    path(
        "registration/",
        views.registration,
        name="registration",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # ==========================================
    # ENROLLMENT
    # ==========================================

    path(
        "enroll/<int:course_id>/",
        views.start_enrollment,
        name="start_enrollment",
    ),

    path(
        "enrollment/details/",
        views.enrollment_details,
        name="enrollment_details",
    ),

    path(
        "enrollment/success/<int:enrollment_id>/",
        views.enrollment_success,
        name="enrollment_success",
    ),

    # ==========================================
    # CHECKOUT
    # ==========================================

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    # ==========================================
    # PAYMENT
    # ==========================================

    path(
        "payment/",
        views.payment_page,
        name="payment_page",
    ),

    path(
        "success/",
        views.payment_success,
        name="payment_success",
    ),

    path(
        "receipt/<str:receipt_number>/",
        views.payment_receipt,
        name="payment_receipt",
    ),
]