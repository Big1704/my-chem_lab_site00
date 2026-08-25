from django.urls import path
from . import views

urlpatterns = [
    # 🏠 หน้าแรก
    path('', views.home, name='home'),
    
    # 📚 หมวดหมู่เรียนรู้
    path('glassware/', views.glassware_list, name='glassware_list'),
    path('instruments/', views.instrument_list, name='instrument_list'),
    path('equipment/<int:pk>/', views.detail, name='detail'),
    path('equipment/<int:pk>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # 📝 แบบทดสอบก่อนเรียน (Pre-test)
    path('pre-test/', views.quiz_pretest, name='quiz_pretest'),
    path('pre-test/submit/', views.submit_quiz_pretest, name='submit_quiz_pretest'),
    path('pre-test/result/<int:pk>/', views.quiz_pretest_result, name='quiz_pretest_result'),
    
    # 🎯 แบบทดสอบหลังเรียน (Post-test 40 ข้อ)
    path('quiz-40/', views.quiz_40, name='quiz_40'),
    path('quiz-40/submit/', views.submit_quiz_40, name='submit_quiz_40'),
    path('quiz-40/result/<int:pk>/', views.quiz_40_result, name='quiz_40_result'),
    
    # 👤 ระบบผู้ใช้งาน และ Dashboard
    path('signup/', views.signup, name='signup'),
    path('my-scores/', views.my_scores, name='my_scores'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]