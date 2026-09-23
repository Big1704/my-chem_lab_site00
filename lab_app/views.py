import random
import re
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Equipment, Quiz40Result, QuizPreTestResult, QuizResult
from .quiz_data import QUIZ_50_QUESTIONS


# Helper Function: ดึงข้อมูลข้อสอบจากคลังตาม List ของ ID ที่สุ่มได้
def get_questions_by_ids(q_ids):
    q_map = {q['id']: q for q in QUIZ_50_QUESTIONS}
    return [q_map[qid] for qid in q_ids if qid in q_map]


# Helper Function: เช็กสิทธิ์ Admin/Staff
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


# 3. หน้ารายละเอียดเครื่องแก้วแต่ละชิ้น
def detail(request, pk):
    item = get_object_or_404(Equipment, pk=pk, category='glassware')
    return render(request, 'lab_app/detail.html', {'item': item})


# --- 📝 แบบทดสอบก่อนเรียน (Pre-test สุ่ม 40 จาก 50 ข้อ) ---


# 4. หน้าแสดงทำแบบทดสอบก่อนเรียน
@login_required(login_url='login')
def quiz_pretest(request):
    # สุ่มข้อสอบ 40 ข้อ จากคลัง 50 ข้อ
    selected_questions = random.sample(
        QUIZ_50_QUESTIONS, min(40, len(QUIZ_50_QUESTIONS))
    )

    # บันทึก ID ข้อสอบที่สุ่มได้ลงใน Session
    request.session['pretest_q_ids'] = [q['id'] for q in selected_questions]

    return render(
        request, 'lab_app/quiz_pretest.html', {'questions': selected_questions}
    )


# 5. ประมวลผลแบบทดสอบก่อนเรียน (ไม่มีเกณฑ์ผ่าน บันทึกลง DB)
@login_required(login_url='login')
def submit_quiz_pretest(request):
    if request.method == 'POST':
        # ดึง ID ข้อสอบชุดที่สุ่มได้จาก Session
        q_ids = request.session.get('pretest_q_ids', [])
        if not q_ids:
            return redirect('quiz_pretest')

        questions = get_questions_by_ids(q_ids)
        score = 0
        user_answers = {}

        for q in questions:
            q_id = str(q['id'])
            selected = request.POST.get(f'q_{q_id}')
            user_answers[q_id] = selected

            if selected == q['correct']:
                score += 1

        total = len(questions)
        percent = (score / total) * 100 if total > 0 else 0

        result = QuizPreTestResult.objects.create(
            user=request.user,
            score=score,
            total_questions=total,
            percentage=percent,
            user_answers=user_answers,
        )

        # ลบ Session เมื่อประมวลผลเสร็จสิ้น
        if 'pretest_q_ids' in request.session:
            del request.session['pretest_q_ids']

        return redirect('quiz_pretest_result', pk=result.pk)
    return redirect('quiz_pretest')


# 6. หน้าแสดงผลคะแนนก่อนเรียน และเฉลยข้อที่ทำผิด
@login_required(login_url='login')
def quiz_pretest_result(request, pk):
    result = get_object_or_404(QuizPreTestResult, pk=pk, user=request.user)

    q_map = {str(q['id']): q for q in QUIZ_50_QUESTIONS}
    wrong_questions = []

    for q_id, user_choice in result.user_answers.items():
        q = q_map.get(q_id)
        if q and user_choice != q['correct']:
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


# --- 🌟 แบบทดสอบหลังเรียน (Post-test สุ่ม 40 จาก 50 ข้อ) ---


# 7. หน้าแสดงทำแบบทดสอบหลังเรียน
@login_required(login_url='login')
def quiz_40(request):
    # สุ่มข้อสอบ 40 ข้อใหม่แยกต่างหาก
    selected_questions = random.sample(
        QUIZ_50_QUESTIONS, min(40, len(QUIZ_50_QUESTIONS))
    )

    # บันทึก ID ข้อสอบลงใน Session
    request.session['posttest_q_ids'] = [q['id'] for q in selected_questions]

    return render(
        request, 'lab_app/quiz_40.html', {'questions': selected_questions}
    )


# 8. ประมวลผลแบบทดสอบหลังเรียน (มีเกณฑ์ผ่าน 80% / 32 ข้อ บันทึกลง DB)
@login_required(login_url='login')
def submit_quiz_40(request):
    if request.method == 'POST':
        q_ids = request.session.get('posttest_q_ids', [])
        if not q_ids:
            return redirect('quiz_40')

        questions = get_questions_by_ids(q_ids)
        score = 0
        user_answers = {}

        for q in questions:
            q_id = str(q['id'])
            selected = request.POST.get(f'q_{q_id}')
            user_answers[q_id] = selected

            if selected == q['correct']:
                score += 1

        total = len(questions)
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

        if 'posttest_q_ids' in request.session:
            del request.session['posttest_q_ids']

        return redirect('quiz_40_result', pk=result.pk)
    return redirect('quiz_40')


# 9. หน้าแสดงผลคะแนนหลังเรียน และเฉลยข้อที่ทำผิด
@login_required(login_url='login')
def quiz_40_result(request, pk):
    result = get_object_or_404(Quiz40Result, pk=pk, user=request.user)

    q_map = {str(q['id']): q for q in QUIZ_50_QUESTIONS}
    wrong_questions = []

    for q_id, user_choice in result.user_answers.items():
        q = q_map.get(q_id)
        if q and user_choice != q['correct']:
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


# 10. [สำหรับ User] หน้าดูคะแนนตนเอง
@login_required(login_url='login')
def my_scores(request):
    results = Quiz40Result.objects.filter(user=request.user).order_by(
        '-date_taken'
    )
    pretest_results = QuizPreTestResult.objects.filter(
        user=request.user
    ).order_by('-date_taken')

    latest_pretest = pretest_results.first()
    latest_posttest = results.first()

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
        'results': results,
        'pretest_results': pretest_results,
        'latest_pretest': latest_pretest,
        'latest_posttest': latest_posttest,
        'progress_data': progress_data,
    }
    return render(request, 'lab_app/my_scores.html', context)


# 11. บันทึกคะแนนแบบทดสอบรายชิ้น
@login_required(login_url='login')
def submit_quiz(request, pk):
    if request.method == 'POST':
        score = request.POST.get('score')
        item = get_object_or_404(Equipment, pk=pk, category='glassware')
        QuizResult.objects.create(
            user=request.user, equipment=item, score=score
        )
    return redirect('home')


# 12. สมัครสมาชิก
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# 13. [สำหรับ Admin] หน้า Dashboard สรุปผลสอบผู้ใช้งานทั้งหมด
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