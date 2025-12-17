from .models import Student, Group

def generate_groups(section, num_groups, weights=None):
    """
    Implements Greedy Partitioning with Weighted Skills for a SPECIFIC Section.
    """
    if weights is None:
        weights = {'c': 1, 'd': 1, 'w': 1, 'p': 1}

    # 1. Reset Groups ONLY for this section
    Group.objects.filter(section=section).delete()
    
    # 2. Fetch students ONLY for this section
    all_students = list(Student.objects.filter(section=section))
    if not all_students:
        return

    # 3. Create Groups linked to this section
    groups = []
    for i in range(num_groups):
        new_group = Group.objects.create(name=f"Group {i+1}", section=section)
        groups.append({
            'object': new_group,
            'current_weighted_score': 0 
        })

    # 4. Helper to calculate weighted power
    def get_power(s):
        return (s.coding * weights['c']) + \
               (s.design * weights['d']) + \
               (s.writing * weights['w']) + \
               (s.presenting * weights['p'])

    # 5. Sort students
    all_students.sort(key=get_power, reverse=True)

    # 6. Assign
    for student in all_students:
        student_power = get_power(student)
        weakest_group = min(groups, key=lambda g: g['current_weighted_score'])
        
        student.assigned_group = weakest_group['object']
        student.save()
        
        weakest_group['current_weighted_score'] += student_power