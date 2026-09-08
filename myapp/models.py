from django.db import models


# category table
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    
    # icon lagane ke liye
    icon = models.CharField(
        max_length=80, 
        blank=True, 
        default="fa-solid fa-layer-group", 
        help_text="icon ka naam dalo jaise: fa-solid fa-code"
    )

    class Meta:
        verbose_name_plural = "Categories" # admin me spelling theek karne ke liye
        ordering = ["name"]

    def __str__(self):
        return self.name


# course ki details yaha aayengi
class Course(models.Model):
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    price = models.PositiveIntegerField() # course ki fees
    description = models.TextField(blank=True, default="")
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# topic wala table
class Topic(models.Model):
    name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")

    def __str__(self):
        return self.name


# extra options jaise weekend batch, wagera
class CourseOption(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=120, help_text="Ex: Weekend Batch ya Certificate")
    description = models.CharField(max_length=240, blank=True, default="")
    
    # agar koi extra fees hai toh yaha add hogi
    price_delta = models.IntegerField(default=0, help_text="extra paise jo add honge, free hai to 0 rakho")
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.course.name + " - " + self.name


# student registration form ka data
class Registration(models.Model):
    fullname = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    dob = models.DateField(blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    
    # password match check karne ke liye
    confirm_password = models.CharField(max_length=255, blank=True, default="") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Payment(models.Model):
    student = models.ForeignKey(
        Registration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    receipt_number = models.CharField(max_length=50, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, unique=True)
    razorpay_order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=30, default="paid")
    method = models.CharField(max_length=30, blank=True, default="")
    bank = models.CharField(max_length=100, blank=True, default="")
    wallet = models.CharField(max_length=100, blank=True, default="")
    vpa = models.CharField(max_length=150, blank=True, default="")
    card_last4 = models.CharField(max_length=4, blank=True, default="")
    card_network = models.CharField(max_length=40, blank=True, default="")
    paid_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return self.receipt_number


class PaymentItem(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="items",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    course_name = models.CharField(max_length=200)
    options = models.CharField(max_length=300, blank=True, default="")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.course_name

class StudentProfile(models.Model):
    student = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True, default="")
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True, default="")
    email = models.EmailField(max_length=254)
    dob = models.DateField()
    gender = models.CharField(max_length=20, blank=True, default="")
    current_study = models.CharField(max_length=150)
    highest_qualification = models.CharField(max_length=150, blank=True, default="")
    institute_name = models.CharField(max_length=180, blank=True, default="")
    occupation_status = models.CharField(max_length=40, default="student")
    job_title = models.CharField(max_length=120, blank=True, default="")
    company_name = models.CharField(max_length=150, blank=True, default="")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address = models.TextField()
    guardian_name = models.CharField(max_length=120, blank=True, default="")
    emergency_contact = models.CharField(max_length=15, blank=True, default="")
    aadhaar_last4 = models.CharField(max_length=4, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Enrollment(models.Model):
    student = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(max_length=30, default="registered")
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

