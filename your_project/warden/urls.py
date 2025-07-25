from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome_page'),  # Empty string ('') makes this the homepage
    path('about/',views.about, name='about'),
    path('contact/',views.contact, name='contact'),
    path('login/', views.warden_login, name='warden_login'),
    path('home/signup/', views.signup, name='signup'),
    path('signup/', views.signup, name='signup'),
    path('register_student/', views.register_student, name='register_student'),
    path('studashboard/', views.studashboard, name='studashboard'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('check_in/<int:student_id>/', views.check_in, name='check_in'),
    path('checked-in-students/', views.checked_in_students, name='checked_in_students'),
    path('check_out/<int:student_id>/', views.check_out, name='check_out'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('warden/dashboard/', views.warden_dashboard, name='warden_dashboard'),
    path('report/',views.report,name='report'),
    path('generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),
     
   
]


