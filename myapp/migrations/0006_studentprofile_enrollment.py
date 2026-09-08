import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0005_registration_dob_payment_paymentitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=80)),
                ("middle_name", models.CharField(blank=True, default="", max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("phone", models.CharField(max_length=15)),
                ("alternate_phone", models.CharField(blank=True, default="", max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("dob", models.DateField()),
                ("gender", models.CharField(blank=True, default="", max_length=20)),
                ("current_study", models.CharField(max_length=150)),
                ("highest_qualification", models.CharField(blank=True, default="", max_length=150)),
                ("institute_name", models.CharField(blank=True, default="", max_length=180)),
                ("occupation_status", models.CharField(default="student", max_length=40)),
                ("job_title", models.CharField(blank=True, default="", max_length=120)),
                ("company_name", models.CharField(blank=True, default="", max_length=150)),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("pincode", models.CharField(max_length=10)),
                ("address", models.TextField()),
                ("guardian_name", models.CharField(blank=True, default="", max_length=120)),
                ("emergency_contact", models.CharField(blank=True, default="", max_length=15)),
                ("aadhaar_last4", models.CharField(blank=True, default="", max_length=4)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to="myapp.registration")),
            ],
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(default="registered", max_length=30)),
                ("email_sent", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="myapp.course")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="myapp.registration")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(fields=("student", "course"), name="unique_student_course_enrollment"),
        ),
    ]
