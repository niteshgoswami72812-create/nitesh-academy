from django.test import TestCase
from django.urls import reverse

from .models import Category, Course, CourseOption, Registration


class AcademyExperienceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Full Stack")
        self.course = Course.objects.create(
            name="Django Product Builder",
            duration="12 Weeks",
            price=14999,
            category=self.category,
        )
        self.option = CourseOption.objects.create(
            course=self.course,
            name="Weekend Batch",
            price_delta=2000,
        )

    def test_home_displays_featured_course(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Product Builder")

    def test_courses_page_displays_categories(self):
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All categories")
        self.assertContains(response, "Full Stack")

    def test_category_page_displays_its_courses(self):
        response = self.client.get(reverse("category_courses", args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Product Builder")

    def test_course_detail_displays_options(self):
        response = self.client.get(reverse("course_detail", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weekend Batch")
        self.assertContains(response, "Choose your options")

    def test_custom_session_login_is_reflected_in_header(self):
        user = Registration.objects.create(
            fullname="Nitesh Kumar",
            email="nitesh@example.com",
            username="nitesh",
            password="unused-for-this-test",
        )
        session = self.client.session
        session["registration_user_id"] = user.id
        session["registration_fullname"] = user.fullname
        session.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Hi, Nitesh Kumar")
        self.assertContains(response, "Logout")
