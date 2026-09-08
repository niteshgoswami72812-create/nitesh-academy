from django import forms
from django.forms import inlineformset_factory

from .models import (
    Category,
    Course,
    Topic,
    CourseOption,
    StudentProfile,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "icon",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Category name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Category description",
                }
            ),

            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fa-solid fa-code",
                }
            ),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = [
            "name",
            "duration",
            "price",
            "description",
            "category",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Course name",
                }
            ),

            "duration": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 6 Months",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Course price",
                    "min": "0",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Course description",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic

        fields = [
            "name",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Topic name",
                }
            ),
        }


class CourseOptionForm(forms.ModelForm):
    class Meta:
        model = CourseOption

        fields = [
            "name",
            "description",
            "price_delta",
            "is_default",
            "is_active",
            "sort_order",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Weekend Batch",
                }
            ),

            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Option description",
                }
            ),

            "price_delta": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Extra price",
                }
            ),

            "sort_order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }


TopicFormSet = inlineformset_factory(
    Course,
    Topic,
    form=TopicForm,
    extra=1,
    can_delete=True,
)


CourseOptionFormSet = inlineformset_factory(
    Course,
    CourseOption,
    form=CourseOptionForm,
    extra=1,
    can_delete=True,
)

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "dob",
            "phone",
            "alternate_phone",
            "email",
            "gender",
            "current_study",
            "highest_qualification",
            "institute_name",
            "occupation_status",
            "job_title",
            "company_name",
            "city",
            "state",
            "pincode",
            "address",
            "guardian_name",
            "emergency_contact",
            "aadhaar_last4",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "middle_name": forms.TextInput(attrs={"placeholder": "Middle name (optional)"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "dob": forms.DateInput(attrs={"type": "date"}),
            "phone": forms.TextInput(attrs={"placeholder": "10 digit mobile number", "maxlength": "10"}),
            "alternate_phone": forms.TextInput(attrs={"placeholder": "Alternate number (optional)", "maxlength": "10"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "gender": forms.Select(choices=[("", "Select"), ("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not", "Prefer not to say")]),
            "current_study": forms.TextInput(attrs={"placeholder": "Example: B.Tech 3rd Year / Class 12 / Working"}),
            "highest_qualification": forms.TextInput(attrs={"placeholder": "Highest qualification"}),
            "institute_name": forms.TextInput(attrs={"placeholder": "School / College / Institute"}),
            "occupation_status": forms.Select(choices=[("student", "Student"), ("working", "Working"), ("self_employed", "Self-employed"), ("not_working", "Not working")]),
            "job_title": forms.TextInput(attrs={"placeholder": "Job title (if working)"}),
            "company_name": forms.TextInput(attrs={"placeholder": "Company name (if working)"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "state": forms.TextInput(attrs={"placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"placeholder": "PIN code", "maxlength": "6"}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Current address"}),
            "guardian_name": forms.TextInput(attrs={"placeholder": "Parent / Guardian name (optional)"}),
            "emergency_contact": forms.TextInput(attrs={"placeholder": "Emergency contact (optional)", "maxlength": "10"}),
            "aadhaar_last4": forms.TextInput(attrs={"placeholder": "Aadhaar last 4 digits only (optional)", "maxlength": "4"}),
        }

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if not value.isdigit() or len(value) != 10:
            raise forms.ValidationError("Enter a valid 10 digit mobile number.")
        return value

    def clean_pincode(self):
        value = self.cleaned_data["pincode"].strip()
        if not value.isdigit() or len(value) != 6:
            raise forms.ValidationError("Enter a valid 6 digit PIN code.")
        return value

    def clean_aadhaar_last4(self):
        value = self.cleaned_data.get("aadhaar_last4", "").strip()
        if value and (not value.isdigit() or len(value) != 4):
            raise forms.ValidationError("Enter only the last 4 digits of Aadhaar.")
        return value

