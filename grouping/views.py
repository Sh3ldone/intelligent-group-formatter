from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Group, Student, Section
from .services import generate_groups
from .forms import StudentForm, SectionForm, TeacherSignUpForm  
import statistics

 

@login_required
def section_list(request):
    """Shows the list of classes created by the logged-in teacher."""
    sections = Section.objects.filter(teacher=request.user)
    form = SectionForm()
    return render(request, 'grouping/section_list.html', {'sections': sections, 'form': form})

@login_required
def add_section(request):
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.teacher = request.user
            section.save()
    return redirect('section_list')

@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        section.delete()
    return redirect('section_list')

# --- DASHBOARD & GROUPING ---

@login_required
def dashboard(request, section_id):
    # Ensure the teacher owns this section
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    
    # Filter groups and students by SECTION
    groups = Group.objects.filter(section=section).prefetch_related('students')
    all_students = Student.objects.filter(section=section).order_by('name')
    form = StudentForm()

    group_data = []
    for group in groups:
        students = group.students.all()

        # 1. Stats for Charts
        stats = students.aggregate(c=Sum('coding'), d=Sum('design'), w=Sum('writing'), p=Sum('presenting'))
        skill_values = [stats['c'] or 0, stats['d'] or 0, stats['w'] or 0, stats['p'] or 0]
        
        # --- NEW SMART LOGIC: WEAKNESS DETECTION ---
        skill_labels = ['Coding', 'Design', 'Writing', 'Speaking']
        weakness = None # Default to None
        
        # Only calculate if there are students
        if sum(skill_values) > 0:
            min_score = min(skill_values)
            max_score = max(skill_values)
            
            # LOGIC FIX: If all skills are equal (e.g. 5,5,5,5), don't show a weakness
            if min_score < max_score: 
                # Pair the scores: [('Coding', 10), ('Design', 5)...]
                zipped_skills = list(zip(skill_labels, skill_values))
                
                # Find the skill with the minimum score
                min_skill = min(zipped_skills, key=lambda x: x[1])
                
                weakness = f"{min_skill[0]} ({min_skill[1]} pts)"
        # -------------------------------------

        # 2. Conflict Detection Logic
        student_totals = [s.coding + s.design + s.writing + s.presenting for s in students]
        compatibility_score = 0
        is_unbalanced = False
        suggestion = None

        if len(student_totals) > 1:
            compatibility_score = statistics.stdev(student_totals)
            if compatibility_score > 4.0:
                is_unbalanced = True
                avg_skill = statistics.mean(student_totals)
                outlier = max(students, key=lambda s: abs((s.coding+s.design+s.writing+s.presenting) - avg_skill))
                suggestion = f"Try moving {outlier.name}"

        group_data.append({
            'group': group,
            'skill_values': skill_values,
            'compatibility_score': compatibility_score,
            'is_unbalanced': is_unbalanced,
            'suggestion': suggestion,
            'weakness': weakness 
        })
    
    return render(request, 'grouping/dashboard.html', {
        'section': section,
        'group_data': group_data, 
        'all_students': all_students,
        'form': form  
    })

@login_required
def trigger_generation(request, section_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        k_value = int(request.POST.get('group_count', 2))
        weights = {
            'c': int(request.POST.get('weight_c', 1)),
            'd': int(request.POST.get('weight_d', 1)),
            'w': int(request.POST.get('weight_w', 1)),
            'p': int(request.POST.get('weight_p', 1)),
        }
        
        # --- NEW LOGIC: FORCE RESET ---
        # 1. Check if we already have groups.
        existing_groups = Group.objects.filter(section=section)
        
        # 2. If the user is asking for a DIFFERENT number of groups (e.g., has 2, asks for 3)
        #    OR if they clicked the button (implying they want a re-do),
        #    we delete the old ones first.
        if existing_groups.exists():
            existing_groups.delete()  # <--- Force Delete old groups
            
        # 3. Now call the service (The Safety Check in services.py won't block us because we deleted them)
        generate_groups(section, k_value, weights)
        
    return redirect('dashboard', section_id=section_id)

@login_required
def add_student(request, section_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.section = section
            student.save()
    return redirect('dashboard', section_id=section_id)

@login_required
def clear_data(request, section_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        # Only delete data for THIS section
        Student.objects.filter(section=section).delete()
        Group.objects.filter(section=section).delete()
    return redirect('dashboard', section_id=section_id)

@login_required
def move_student(request, section_id, student_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id, section=section)
        new_group_id = request.POST.get('new_group_id')
        if new_group_id:
            new_group = get_object_or_404(Group, id=new_group_id, section=section)
            student.assigned_group = new_group
            student.save()
    return redirect('dashboard', section_id=section_id)

@login_required
def delete_students(request, section_id):
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    if request.method == "POST":
        student_ids = request.POST.getlist('student_ids')
        Student.objects.filter(id__in=student_ids, section=section).delete()
    return redirect('dashboard', section_id=section_id)

# --- AUTHENTICATION ---

def signup(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST) # <--- Uses Custom Form
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('section_list') 
    else:
        form = TeacherSignUpForm() # <--- Uses Custom Form
    return render(request, 'registration/signup.html', {'form': form})