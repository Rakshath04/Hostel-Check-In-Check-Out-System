from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import Student, CheckInCheckOut
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

# Signup/Warden login view
def warden_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('warden_dashboard')
        else:
            return render(request, 'warden/login.html', {'error': 'Invalid credentials'})
    pass   
    return render(request, 'warden/login.html')


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def warden_dashboard(request):
    return render(request, 'warden/warden_dashboard.html')




# Signup view for Warden
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warden_login')
    else:
        form = UserCreationForm()
    pass    
    return render(request, 'warden/signup.html', {'form': form})




# New student registration view
@login_required
def register_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        roll_number = request.POST['roll_number']
        dob = request.POST['dob']
        
        # Check if the roll_number already exists
        if Student.objects.filter(roll_number=roll_number).exists():
            # You can handle duplicate roll number here
            return render(request, 'warden/register_student.html', {'error': 'Roll number already exists.'})
        
        # If the roll number is unique, save the student
        student = Student(name=name, roll_number=roll_number, dob=dob)
        student.save()
        return redirect('warden_dashboard')  # Redirect to the dashboard after registration
    
        pass
    return render(request, 'warden/register_student.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentForm

@login_required
def studashboard(request):
    query = request.GET.get('search', '')  # Get the search query from URL parameters

    if query:
        # Search for students by roll number (case-insensitive)
        students = Student.objects.filter(roll_number__icontains=query)
    else:
        # Show all students if no search query
        students = Student.objects.all()

    # Handle student deletion
    if request.method == 'POST' and 'delete' in request.POST:
        student_id = request.POST['delete']
        student = Student.objects.get(id=student_id)
        student.delete()
        return redirect('studashboard')  # Redirect to refresh the student list

    return render(request, 'warden/studashboard.html', {'students': students, 'search': query})

@login_required
def edit_student(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('studashboard')  # Redirect back to student dashboard after saving

    else:
        form = StudentForm(instance=student)

    return render(request, 'warden/edit_student.html', {'form': form, 'student': student})




# Check-in a student
@login_required
def check_in(request, student_id):
    student = Student.objects.get(id=student_id)
    
    # Create a new check-in record for the student
    check_in_record = CheckInCheckOut.objects.create(
        student=student,
        check_in_time=timezone.now(),
    )

    return redirect('warden_dashboard')

# Check-out a student
@login_required
def check_out(request, student_id):
    student = Student.objects.get(id=student_id)
    check_in_record = CheckInCheckOut.objects.filter(student=student, check_out_time__isnull=True).last()
    
    if check_in_record:
        check_in_record.check_out_time = timezone.now()
        check_in_record.save()

        check_in_record.delete()
        
    return redirect('warden_dashboard')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required
def dashboard(request):
    search_query = request.GET.get('search', '')  # Get the search query from the request

    # Query to fetch all students from the database
    query = "SELECT * FROM warden_student"
    with connection.cursor() as cursor:
        cursor.execute(query)
        students = cursor.fetchall()

    # Filter students by roll number if search query is provided
    if search_query:
        students = [student for student in students if search_query.lower() in str(student[2]).lower()]

    student_status = []
    for student in students:
        student_id = student[0]  # Assuming the first column is the student ID
        query_status = """
            SELECT check_in_time, check_out_time
            FROM warden_checkincheckout 
            WHERE student_id = %s ORDER BY check_in_time DESC LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(query_status, [student_id])
            status = cursor.fetchone()
            student_status.append({
                'student': student,
                'check_in_time': status[0] if status else None,
            })

    context = {
        'student_status': student_status,
        'search_query': search_query,  # Pass the search query to the template
    }
    pass
    return render(request, 'warden/dashboard.html', context)




@login_required
def checked_in_students(request):
    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')  # Default to empty string if no search query

    # Get all students, or filter based on the search query if provided
    if search_query:
        students = Student.objects.filter(roll_number__icontains=search_query)
    else:
        students = Student.objects.all()

    checked_in_students = []
    for student in students:
        # Get the most recent check-in record for the student where check_out_time is null (student is checked in)
        check_in_record = CheckInCheckOut.objects.filter(student=student, check_out_time__isnull=True).last()
        
        if check_in_record:
            checked_in_students.append({
                'student': student,
                'check_in_time': check_in_record.check_in_time
            })

    context = {
        'checked_in_students': checked_in_students,
        'search': search_query  # Pass the search term to the template for pre-population
    }
    pass
    return render(request, 'warden/checked_in_students_dashboard.html', context)


from django.shortcuts import render

# View function for the Welcome Page
def welcome_page(request):
    return render(request, 'warden/welcome_page.html')




# View function for the about Page
def about(request):
    return render(request, 'warden/about.html')



# View function for the contact Page
def contact(request):
    return render(request, 'warden/contact.html')



@login_required
def report(request):
    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')  # Default to empty string if no search query

    # Get all students, or filter based on the search query if provided
    if search_query:
        students = Student.objects.filter(roll_number__icontains=search_query)
    else:
        students = Student.objects.all()

    checked_in_students = []
    for student in students:
        # Get the most recent check-in record for the student where check_out_time is null (student is checked in)
        check_in_record = CheckInCheckOut.objects.filter(student=student, check_out_time__isnull=True).last()
        
        if check_in_record:
            checked_in_students.append({
                'student': student,
                'check_in_time': check_in_record.check_in_time
            })

    context = {
        'checked_in_students': checked_in_students,
        'search': search_query  # Pass the search term to the template for pre-population
    }
    pass
    return render(request, 'warden/report.html', context)




from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Student, CheckInCheckOut
from django.shortcuts import render

@login_required
def generate_pdf_report(request):
    # Get checked-in students
    checked_in_students = []
    students = Student.objects.all()

    for student in students:
        check_in_record = CheckInCheckOut.objects.filter(student=student, check_out_time__isnull=True).last()
        if check_in_record:
            checked_in_students.append({
                'name': student.name,
                'roll_number': student.roll_number,
                'check_in_time': check_in_record.check_in_time
            })

    # Create response object for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="checked_in_students_report.pdf"'

    # Create PDF with the data
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Page size for letter format

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 40, "Checked-In Students Report")

    # Table Header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, height - 80, "Name")
    pdf.drawString(300, height - 80, "Roll Number")
    pdf.drawString(500, height - 80, "Check-in Time")

    # Table Data
    pdf.setFont("Helvetica", 10)
    y_position = height - 100
    for student in checked_in_students:
        pdf.drawString(100, y_position, student['name'])
        pdf.drawString(300, y_position, student['roll_number'])
        pdf.drawString(500, y_position, str(student['check_in_time']))
        y_position -= 20

        # Prevent content from going off the page
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = height - 40

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    return response

