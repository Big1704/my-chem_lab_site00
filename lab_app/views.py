from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Equipment, QuizResult, Quiz40Result
from .quiz_data import QUIZ_40_QUESTIONS

# Helper Function เช็กสิทธิ์ Admin/Staff
def is_admin(user):
    return user.is_staff or user.is_superuser


# 1. หน้าแรก (แสดงเมนูหลัก)
def home(request):
    return render(request, 'lab_app/home.html')


# 2. หน้าแสดงเฉพาะเครื่องแก้ว
def glassware_list(request):
    items = Equipment.objects.filter(category='glassware')
    context = {
        'items': items,
        'title': '🧪 เครื่องแก้ว (Glassware)',
        'category_color': 'primary'
    }
    return render(request, 'lab_app/equipment_list.html', context)


# 3. หน้าแสดงเฉพาะเครื่องมือวิทยาศาสตร์
def instrument_list(request):
    items = Equipment.objects.filter(category='instrument')
    context = {
        'items': items,
        'title': '🔬 เครื่องมือวิทยาศาสตร์ (Instruments)',
        'category_color': 'success'
    }
    return render(request, 'lab_app/equipment_list.html', context)


# 4. หน้ารายละเอียดอุปกรณ์แต่ละชิ้น
def detail(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    return render(request, 'lab_app/detail.html', {'item': item})


# 5. หน้าแสดงทำแบบทดสอบ 40 ข้อ (ต้องล็อกอินเท่านั้น)
@login_required(login_url='login')
def quiz_40(request):
    return render(request, 'lab_app/quiz_40.html', {'questions': QUIZ_40_QUESTIONS})


# 6. ประมวลผลแบบทดสอบ 40 ข้อ
@login_required(login_url='login')
def submit_quiz_40(request):
    if request.method == "POST":
        score = 0
        user_answers = {}

        for q in QUIZ_40_QUESTIONS:
            q_id = str(q['id'])
            selected = request.POST.get(f"q_{q_id}")
            user_answers[q_id] = selected

            if selected == q['correct']:
                score += 1

        total = len(QUIZ_40_QUESTIONS)
        percent = (score / total) * 100
        is_passed = score >= 32  # 80% ของ 40 ข้อ คือ 32 ข้อ

        # บันทึกลงฐานข้อมูล
        result = Quiz40Result.objects.create(
            user=request.user,
            score=score,
            total_questions=total,
            percentage=percent,
            passed=is_passed,
            user_answers=user_answers
        )

        return redirect('quiz_40_result', pk=result.pk)
    return redirect('quiz_40')


# 7. หน้าแสดงผลคะแนน และเฉลยข้อที่ทำผิด
@login_required(login_url='login')
def quiz_40_result(request, pk):
    result = get_object_or_404(Quiz40Result, pk=pk, user=request.user)
    
    # รวบรวมข้อที่ทำผิดและเฉลย
    wrong_questions = []
    for q in QUIZ_40_QUESTIONS:
        q_id = str(q['id'])
        user_choice = result.user_answers.get(q_id)
        if user_choice != q['correct']:
            wrong_questions.append({
                'id': q['id'],
                'question': q['question'],
                'options': q['options'],
                'user_choice': user_choice,
                'user_choice_text': q['options'].get(user_choice, 'ไม่ได้ตอบ') if user_choice else 'ไม่ได้ตอบ',
                'correct_choice': q['correct'],
                'correct_choice_text': q['options'].get(q['correct'])
            })

    context = {
        'result': result,
        'wrong_questions': wrong_questions,
        'total_wrong': len(wrong_questions)
    }
    return render(request, 'lab_app/quiz_40_result.html', context)


# 8. บันทึกคะแนนแบบทดสอบรายชิ้น
@login_required
def submit_quiz(request, pk):
    if request.method == "POST":
        score = request.POST.get('score')
        item = get_object_or_404(Equipment, pk=pk)
        QuizResult.objects.create(user=request.user, equipment=item, score=score)
    return redirect('home')


# 9. สมัครสมาชิก
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# 10. [สำหรับ User] หน้าดูคะแนนตัวเอง
@login_required
def my_scores(request):
    user_results = Quiz40Result.objects.filter(user=request.user).order_by('-date_taken')
    return render(request, 'lab_app/my_scores.html', {'results': user_results})


# 11. [สำหรับ Admin] หน้า Dashboard สรุปผลสอบผู้ใช้งานทั้งหมด
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    results_40 = Quiz40Result.objects.select_related('user').all().order_by('-date_taken')
    
    total_attempts = results_40.count()
    passed_count = results_40.filter(passed=True).count()
    failed_count = total_attempts - passed_count
    pass_rate = round((passed_count / total_attempts * 100), 1) if total_attempts > 0 else 0

    context = {
        'results_40': results_40,
        'total_attempts': total_attempts,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pass_rate': pass_rate,
    }
    return render(request, 'lab_app/admin_dashboard.html', context)