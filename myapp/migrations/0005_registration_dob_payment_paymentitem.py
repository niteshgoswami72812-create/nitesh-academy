from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_alter_category_icon_alter_courseoption_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="dob",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receipt_number", models.CharField(max_length=50, unique=True)),
                ("razorpay_payment_id", models.CharField(max_length=100, unique=True)),
                ("razorpay_order_id", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("currency", models.CharField(default="INR", max_length=10)),
                ("status", models.CharField(default="paid", max_length=30)),
                ("method", models.CharField(blank=True, default="", max_length=30)),
                ("bank", models.CharField(blank=True, default="", max_length=100)),
                ("wallet", models.CharField(blank=True, default="", max_length=100)),
                ("vpa", models.CharField(blank=True, default="", max_length=150)),
                ("card_last4", models.CharField(blank=True, default="", max_length=4)),
                ("card_network", models.CharField(blank=True, default="", max_length=40)),
                ("paid_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="myapp.registration")),
            ],
            options={"ordering": ["-paid_at"]},
        ),
        migrations.CreateModel(
            name="PaymentItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_name", models.CharField(max_length=200)),
                ("options", models.CharField(blank=True, default="", max_length=300)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("course", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="myapp.course")),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="myapp.payment")),
            ],
        ),
    ]
