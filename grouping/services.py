import statistics
from .models import Group, Student

def generate_groups(section, k_value, weights=None):
    """
    Stable Power Balancing Algorithm:
    1. Safety Check: If groups exist, STOP immediately (Prevents accidental shuffling).
    2. Deterministic Sort: Sorts by Power, then by ID (Ensures same result every time).
    3. Weakest-First Assignment: Balances total power perfectly.
    """
    
    # --- 1. SAFETY CHECK (The Fix for your issue) ---
    # If groups are already made, stop the function. 
    # This prevents the button from "reshuffling" your work.
    if Group.objects.filter(section=section).exists():
        return

    # 2. Create New Groups
    groups = []
    for i in range(k_value):
        groups.append(Group.objects.create(section=section, name=f"Group {i+1}"))
    
    # 3. Get Students (DETERMINISTIC LOADING)
    # We order by 'id' first to ensure the list is exactly the same every time we load it.
    students = list(Student.objects.filter(section=section).order_by('id'))
    if not students:
        return

    # 4. SORTING
    # Sort from Strongest to Weakest. 
    # Python's sort is stable, so ties will keep their ID order. Result is 100% consistent.
    students.sort(key=lambda s: (s.coding + s.design + s.writing + s.presenting), reverse=True)
    
    # Track stats
    group_stats = []
    for i in range(k_value):
        group_stats.append({
            'index': i,
            'total_power': 0,
            'count': 0,
            'coding': 0, 'design': 0, 'writing': 0, 'presenting': 0
        })

    # 5. ASSIGNMENT LOOP (Weakest-First Strategy)
    for student in students:
        student_power = student.coding + student.design + student.writing + student.presenting
        
        # FIND THE BEST GROUP
        min_size = min(g['count'] for g in group_stats)
        
        best_group = None
        best_score = float('inf')
        
        for g in group_stats:
            # RULE 1: Size Constraint (Keep sizes even)
            if g['count'] > min_size:
                penalty = 100000 
            else:
                penalty = 0
            
            # RULE 2: Power Balancing (Fill the Weakest Group)
            penalty += g['total_power']
            
            # RULE 3: Role Clash (Small Tie-Breaker)
            clash_penalty = 0
            skills = {'coding': student.coding, 'design': student.design, 
                      'writing': student.writing, 'presenting': student.presenting}
            best_skill = max(skills, key=skills.get)
            
            # If student is Expert (5) and Group has Expert (>4), add small penalty
            if skills[best_skill] >= 5 and g[best_skill] >= 4:
                clash_penalty = 5 
            
            penalty += clash_penalty

            if penalty < best_score:
                best_score = penalty
                best_group = g
        
        # ASSIGN
        idx = best_group['index']
        target_group = groups[idx]
        student.assigned_group = target_group
        student.save()
        
        # Update Stats
        group_stats[idx]['total_power'] += student_power
        group_stats[idx]['count'] += 1
        group_stats[idx]['coding'] += student.coding
        group_stats[idx]['design'] += student.design
        group_stats[idx]['writing'] += student.writing
        group_stats[idx]['presenting'] += student.presenting