import re
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Equipment, Quiz40Result, QuizPreTestResult, QuizResult
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
        'category_color': 'primary',
    }
    return render(request, 'lab_app/equipment_list.html', context)


# 3. หน้าแสดงเฉพาะเครื่องมือวิทยาศาสตร์
def instrument_list(request):
    items = Equipment.objects.filter(category='instrument')
    context = {
        'items': items,
        'title': '🔬 เครื่องมือวิทยาศาสตร์ (Instruments)',
        'category_color': 'success',
    }
    return render(request, 'lab_app/equipment_list.html', context)


# 4. หน้ารายละเอียดอุปกรณ์แต่ละชิ้น
def detail(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    return render(request, 'lab_app/detail.html', {'item': item})


# --- 📝 แบบทดสอบก่อนเรียน (Pre-test) ---


# 5. หน้าแสดงทำแบบทดสอบก่อนเรียน
@login_required(login_url='login')
def quiz_pretest(request):
    return render(
        request, 'lab_app/quiz_pretest.html', {'questions': QUIZ_40_QUESTIONS}
    )


# 6. ประมวลผลแบบทดสอบก่อนเรียน (ไม่มีเกณฑ์ผ่าน บันทึกลง DB)
@login_required(login_url='login')
def submit_quiz_pretest(request):
    if request.method == 'POST':
        score = 0
        user_answers = {}

        for q in QUIZ_40_QUESTIONS:
            q_id = str(q['id'])
            selected = request.POST.get(f'q_{q_id}')
            user_answers[q_id] = selected

            if selected == q['correct']:
                score += 1

        total = len(QUIZ_40_QUESTIONS)
        percent = (score / total) * 100 if total > 0 else 0

        result = QuizPreTestResult.objects.create(
            user=request.user,
            score=score,
            total_questions=total,
            percentage=percent,
            user_answers=user_answers,
        )

        return redirect('quiz_pretest_result', pk=result.pk)
    return redirect('quiz_pretest')


# 7. หน้าแสดงผลคะแนนก่อนเรียน และเฉลยข้อที่ทำผิด
@login_required(login_url='login')
def quiz_pretest_result(request, pk):
    result = get_object_or_404(QuizPreTestResult, pk=pk, user=request.user)

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
                'user_choice_text': (
                    q['options'].get(user_choice, 'ไม่ได้ตอบ')
                    if user_choice
                    else 'ไม่ได้ตอบ'
                ),
                'correct_choice': q['correct'],
                'correct_choice_text': q['options'].get(q['correct']),
            })

    context = {
        'result': result,
        'wrong_questions': wrong_questions,
        'total_wrong': len(wrong_questions),
    }
    return render(request, 'lab_app/quiz_pretest_result.html', context)


# --- 🌟 แบบทดสอบหลังเรียน (Post-test 40 ข้อ) ---


# 8. หน้าแสดงทำแบบทดสอบหลังเรียน
@login_required(login_url='login')
def quiz_40(request):
    return render(
        request, 'lab_app/quiz_40.html', {'questions': QUIZ_40_QUESTIONS}
    )


# 9. ประมวลผลแบบทดสอบหลังเรียน (มีเกณฑ์ผ่าน 80% / 32 ข้อ บันทึกลง DB)
@login_required(login_url='login')
def submit_quiz_40(request):
    if request.method == 'POST':
        score = 0
        user_answers = {}

        for q in QUIZ_40_QUESTIONS:
            q_id = str(q['id'])
            selected = request.POST.get(f'q_{q_id}')
            user_answers[q_id] = selected

            if selected == q['correct']:
                score += 1

        total = len(QUIZ_40_QUESTIONS)
        percent = (score / total) * 100 if total > 0 else 0
        is_passed = score >= 32  # 80% ของ 40 ข้อ คือ 32 ข้อ

        result = Quiz40Result.objects.create(
            user=request.user,
            score=score,
            total_questions=total,
            percentage=percent,
            passed=is_passed,
            user_answers=user_answers,
        )

        return redirect('quiz_40_result', pk=result.pk)
    return redirect('quiz_40')


# 10. หน้าแสดงผลคะแนนหลังเรียน และเฉลยข้อที่ทำผิด
@login_required(login_url='login')
def quiz_40_result(request, pk):
    result = get_object_or_404(Quiz40Result, pk=pk, user=request.user)

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
                'user_choice_text': (
                    q['options'].get(user_choice, 'ไม่ได้ตอบ')
                    if user_choice
                    else 'ไม่ได้ตอบ'
                ),
                'correct_choice': q['correct'],
                'correct_choice_text': q['options'].get(q['correct']),
            })

    context = {
        'result': result,
        'wrong_questions': wrong_questions,
        'total_wrong': len(wrong_questions),
    }
    return render(request, 'lab_app/quiz_40_result.html', context)


# --- 📊 ระบบสรุปคะแนนและจัดการผู้ใช้งาน ---


# 11. [สำหรับ User] หน้าดูคะแนนตนเอง (แก้ไข Context ให้ตรงกับ template my_scores.html)
@login_required(login_url='login')
def my_scores(request):
    # ดึงประวัติการทำสอบทั้งหมด
    results = Quiz40Result.objects.filter(user=request.user).order_by('-date_taken')
    pretest_results = QuizPreTestResult.objects.filter(user=request.user).order_by('-date_taken')

    # ดึงผลสอบล่าสุด
    latest_pretest = pretest_results.first()
    latest_posttest = results.first()

    # คำนวณพัฒนาการสำหรับการ์ดสรุปผล
    progress_data = None
    if latest_pretest and latest_posttest:
        score_diff = latest_posttest.score - latest_pretest.score
        pct_diff = latest_posttest.percentage - latest_pretest.percentage
        progress_data = {
            'score_diff': score_diff,
            'percentage_diff': abs(pct_diff),
            'is_improved': score_diff > 0,
            'is_equal': score_diff == 0,
        }

    context = {
        'results': results,                  # ตรงกับ {% for row in results %} (ตารางหลังเรียน)
        'pretest_results': pretest_results,  # ตรงกับ {% for row in pretest_results %} (ตารางก่อนเรียน)
        'latest_pretest': latest_pretest,    # สำหรับการ์ดคะแนนก่อนเรียน
        'latest_posttest': latest_posttest,  # สำหรับการ์ดคะแนนหลังเรียน
        'progress_data': progress_data,      # สำหรับการ์ดสรุปพัฒนาการ
    }
    return render(request, 'lab_app/my_scores.html', context)


# 12. บันทึกคะแนนแบบทดสอบรายชิ้น
@login_required(login_url='login')
def submit_quiz(request, pk):
    if request.method == 'POST':
        score = request.POST.get('score')
        item = get_object_or_404(Equipment, pk=pk)
        QuizResult.objects.create(
            user=request.user, equipment=item, score=score
        )
    return redirect('home')


# 13. สมัครสมาชิก
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# 14. [สำหรับ Admin] หน้า Dashboard สรุปผลสอบผู้ใช้งานทั้งหมด
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    results_40 = (
        Quiz40Result.objects.select_related('user').all().order_by('-date_taken')
    )
    pretest_results = (
        QuizPreTestResult.objects.select_related('user')
        .all()
        .order_by('-date_taken')
    )

    total_attempts = results_40.count()
    passed_count = results_40.filter(passed=True).count()
    failed_count = total_attempts - passed_count
    pass_rate = (
        round((passed_count / total_attempts * 100), 1)
        if total_attempts > 0
        else 0
    )

    context = {
        'results_40': results_40,
        'pretest_results': pretest_results,
        'total_attempts': total_attempts,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pass_rate': pass_rate,
    }
    return render(request, 'lab_app/admin_dashboard.html', context)