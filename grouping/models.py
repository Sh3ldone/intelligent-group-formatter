from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Section(models.Model):
    """
    Represents a specific class or section (e.g., 'BSCS-2A').
    Linked to a specific teacher (User) so data is isolated.
    """
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Group(models.Model):
    """
    Represents a formed team within a specific Section.
    """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    """
    Represents a student belonging to a specific Section.
    """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=100)
    
    # Skill Ratings (Scale of 1-5)
    coding = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    design = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writing = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    presenting = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Link to a Group within the same section
    assigned_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.name