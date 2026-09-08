from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("myapp", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="category",
            name="icon",
            field=models.CharField(blank=True, default="fa-solid fa-layer-group", help_text="Font Awesome class, e.g. fa-solid fa-code", max_length=80),
        ),
        migrations.AddField(
            model_name="course",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.CreateModel(
            name="CourseOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Option name, e.g. Weekend Batch, Certificate, Mentorship", max_length=120)),
                ("description", models.CharField(blank=True, default="", max_length=240)),
                ("price_delta", models.IntegerField(default=0, help_text="Extra amount added to the base course price. Use 0 for free.")),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="myapp.course")),
            ],
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.AlterModelOptions(name="category", options={"ordering": ["name"], "verbose_name_plural": "Categories"}),
        migrations.AlterModelOptions(name="course", options={"ordering": ["name"]}),
    ]
