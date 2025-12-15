from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required  # <--- 1. IMPORT THIS
from .models import Group, Student
from .services import generate_groups
from .forms import StudentForm
import statistics
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# <--- 2. ADD DECORATOR TO DASHBOARD (Entry Point)
@login_required
def dashboard(request):
    groups = Group.objects.prefetch_related('students').all()
    all_students = Student.objects.all().order_by('name')
    form = StudentForm()

    group_data = []
    for group in groups:
        students = group.students.all()

        # 1. Stats for Charts
        stats = students.aggregate(c=Sum('coding'), d=Sum('design'), w=Sum('writing'), p=Sum('presenting'))
        skill_values = [stats['c'] or 0, stats['d'] or 0, stats['w'] or 0, stats['p'] or 0]
        
        # 2. Conflict Detection & Suggestion Logic
        student_totals = [s.coding + s.design + s.writing + s.presenting for s in students]
        
        compatibility_score = 0
        is_unbalanced = False
        suggestion = None

        if len(student_totals) > 1:
            compatibility_score = statistics.stdev(student_totals)
            
            # ALERT THRESHOLD: If deviation > 4.0
            if compatibility_score > 4.0:
                is_unbalanced = True
                
                # INTELLIGENT SUGGESTION: Find the "Outlier"
                # Calculate average skill of this group
                avg_skill = statistics.mean(student_totals)
                
                # Find the student whose score is furthest from the average
                outlier = max(students, key=lambda s: abs((s.coding+s.design+s.writing+s.presenting) - avg_skill))
                
                suggestion = f"Try moving {outlier.name}"

        group_data.append({
            'group': group,
            'skill_values': skill_values,
            'compatibility_score': compatibility_score,
            'is_unbalanced': is_unbalanced,
            'suggestion': suggestion 
        })
    
    return render(request, 'grouping/dashboard.html', {
        'group_data': group_data, 
        'all_students': all_students,
        'form': form  
    })

# <--- 3. ADD DECORATOR TO ALL ACTIONS (Security Best Practice)
@login_required
def trigger_generation(request):
    if request.method == "POST":
        k_value = int(request.POST.get('group_count', 2))
        weights = {
            'c': int(request.POST.get('weight_c', 1)),
            'd': int(request.POST.get('weight_d', 1)),
            'w': int(request.POST.get('weight_w', 1)),
            'p': int(request.POST.get('weight_p', 1)),
        }
        generate_groups(k_value, weights)
    return redirect('dashboard')

@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid(): form.save()
    return redirect('dashboard')

@login_required
def clear_data(request):
    if request.method == "POST":
        Student.objects.all().delete()
        Group.objects.all().delete()
    return redirect('dashboard')

@login_required
def move_student(request, student_id):
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id)
        new_group_id = request.POST.get('new_group_id')
        if new_group_id:
            student.assigned_group = Group.objects.get(id=new_group_id)
            student.save()
    return redirect('dashboard')

@login_required
def delete_students(request):
    if request.method == "POST":
        student_ids = request.POST.getlist('student_ids')
        Student.objects.filter(id__in=student_ids).delete()
    return redirect('dashboard')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in immediately after signing up
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})