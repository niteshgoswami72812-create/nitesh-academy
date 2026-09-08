from django.contrib import admin
from .models import Category, Course, CourseOption, Registration, Topic, Payment, PaymentItem

# Django Admin Panel Configuration
# Author: Nitesh
# Institute: Cybrom Technology

# course form ke andar hi topic add karne ke liye
class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1 # ek khali row dikhane ke liye

# course form ke andar course ke options add karne ke liye
class CourseOptionInline(admin.TabularInline):
    model = CourseOption
    extra = 1
    fields = (
        "name",
        "description",
        "price_delta",
        "is_default",
        "is_active",
        "sort_order",
    )

# category ko admin panel me register kiya
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "course_total")
    search_fields = ("name",)

    # total courses kitne hain wo count karke column me dikhane ke liye
    @admin.display(description="Courses")
    def course_total(self, category):
        return category.courses.count()

# main course model ka admin setting
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "duration", "price")
    list_filter = ("category",)
    search_fields = ("name", "description")
    
    # ek sath topic aur option dono form dikhane ke liye inlines use kiya hai
    inlines = [TopicInline, CourseOptionInline]

# course options ko alag se list me manage karne ke liye
@admin.register(CourseOption)
class CourseOptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "course",
        "price_delta",
        "is_default",
        "is_active",
        "sort_order",
    )
    list_filter = ("is_active", "is_default", "course__category")
    search_fields = ("name", "course__name")

# student registration simple tarike se register kiya hai
admin.site.register(Registration)

class PaymentItemInline(admin.TabularInline):
    model = PaymentItem
    extra = 0
    readonly_fields = ("course_name", "options", "quantity", "unit_price", "line_total")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "student", "amount", "method", "status", "paid_at")
    search_fields = ("receipt_number", "razorpay_payment_id", "student__fullname", "student__email")
    list_filter = ("status", "method", "paid_at")
    inlines = [PaymentItemInline]

from .models import StudentProfile, Enrollment

admin.site.register(StudentProfile)
admin.site.register(Enrollment)
