from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('generate/', views.trigger_generation, name='generate_groups'),
    path('add-student/', views.add_student, name='add_student'),
    path('clear/', views.clear_data, name='clear_data'),
    path('move/<int:student_id>/', views.move_student, name='move_student'),
    path('delete/', views.delete_students, name='delete_students'),
    path('signup/', views.signup, name='signup'),
]