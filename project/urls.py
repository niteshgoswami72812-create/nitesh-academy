from django.contrib import admin
from django.urls import path

from myapp import views


urlpatterns = [

    # Django default admin
    path(
        "admin/",
        admin.site.urls,
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

    path(
        "dashboard/enrollments/",
        views.dashboard_enrollments,
        name="dashboard_enrollments",
    ),

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