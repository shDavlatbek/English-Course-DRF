import os
import uuid
from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser
from main.helpers import CustomUserManager


LEVEL_CHOICES = (
    ('a1', 'Elementary (A1)'),
    ('a2', 'Pre-Intermediate (A2)'),
    ('b1', 'Intermediate (B1)'),
    ('b1-b2', 'Upper-Intermediate (B1+)'),
    ('b2', 'Pre-Advanced (B2)'),
)


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)  # make username optional
    email = models.EmailField(_('email address'), unique=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    

class Course(models.Model):
    image = models.ImageField(upload_to='courses/%d/%m/%Y/', null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='a1')
    description = models.TextField(null=True, blank=True)
    content = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.title



class Enrollment(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"



class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.course.title})"



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.text



class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text



class FillInBlankQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='fill_blank_questions')
    text_before = models.CharField(max_length=500)  # Text before the blank
    text_after = models.CharField(max_length=500, blank=True, null=True)  # Text after the blank
    correct_answer = models.CharField(max_length=100)  # Correct option (e.g., "both", "either", "neither")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.text_before} _____ {self.text_after or ''}"


class FillInBlankOption(models.Model):
    question = models.ForeignKey(FillInBlankQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)  # Option text like "both", "either", "neither"
    
    def __str__(self):
        return self.text


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    correct_answers = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    # Optionally, you might want to add a field to store user answers (e.g. a ManyToMany field to Option)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} score: {self.score}"
    
    


def get_image_path(instance, filename):
    """Generate a unique path for uploaded images."""
    ext = filename.split('.')[-1]
    # Create a unique filename with uuid
    filename = f"{uuid.uuid4().hex}.{ext}"
    # Return the upload path
    return os.path.join('uploads', 'tinymce', filename)



class TinyMCEImage(models.Model):
    """Model to store images uploaded through TinyMCE."""
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=get_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title or f"Image {self.id}"
    
    def save(self, *args, **kwargs):
        # If no title is provided, use the original filename
        if not self.title and self.image:
            self.title = os.path.basename(self.image.name)
        super().save(*args, **kwargs)