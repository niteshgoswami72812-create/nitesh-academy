from django.contrib import admin
from django.urls import path
from myapp import views

# yaha saare project ke URL routes define kiye hain
urlpatterns = [
    # admin panel ka url
    path("admin/", admin.site.urls),
    
    # main pages ke links
    path("", views.home, name="home"), # homepage
    path("about/", views.about, name="about"), # about us page
    path("contact/", views.contact, name="contact"), # contact form page
    path("help/", views.help_page, name="help"), # help and support
    
    # courses dikhane ke urls
    path("courses/", views.courses, name="courses"), # sabhi courses ka page
    
    # category pe click karne pe uske courses dikhane ke liye
    path(
        "courses/category/<int:category_id>/",
        views.category_courses,
        name="category_courses",
    ), 
    
    # single course ki poori detail ka page
    path(
        "courses/course/<int:course_id>/",
        views.course_detail,
        name="course_detail",
    ), 
    
    # login aur signup wale urls
    path("registration/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # cart aur payment ke urls
    path("checkout/", views.checkout, name="checkout"), # course buy karne se pehle ka page
    path("payment/", views.payment_page, name="payment_page"), # razorpay ka payment page
    path("success/", views.payment_success, name="payment_success"), # payment success hone ke baad
]