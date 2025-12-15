from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Group(models.Model):
    """
    Represents a formed team (e.g., 'Group 1', 'Group 2').
    """
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    """
    Represents a student with their self-reported skill ratings.
    """
    name = models.CharField(max_length=100)
    
    # Skill Ratings (Scale of 1-5 as per project scope)
    coding = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    design = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    writing = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    presenting = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Link to a Group. 
    # null=True means they start unassigned.
    # on_delete=models.SET_NULL means if we delete a group, the student isn't deleted, just unassigned.
    assigned_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return self.name