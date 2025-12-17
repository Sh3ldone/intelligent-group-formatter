from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),

    # Home / Section List
    path('', views.section_list, name='section_list'),
    path('add-section/', views.add_section, name='add_section'),

    # Dashboard & Logic (Everything is now locked to a section_id)
    path('section/<int:section_id>/', views.dashboard, name='dashboard'),
    path('section/<int:section_id>/generate/', views.trigger_generation, name='generate_groups'),
    path('section/<int:section_id>/add-student/', views.add_student, name='add_student'),
    path('section/<int:section_id>/clear/', views.clear_data, name='clear_data'),
    path('section/<int:section_id>/move/<int:student_id>/', views.move_student, name='move_student'),
    path('section/<int:section_id>/delete/', views.delete_students, name='delete_students'),
    path('delete_section/<int:section_id>/', views.delete_section, name='delete_section'),
]