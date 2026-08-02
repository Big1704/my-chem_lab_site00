from django.urls import path
from . import views

urlpatterns = [
    # หน้าแรก (เมนู 3 ปุ่มหลัก)
    path('', views.home, name='home'),
    
    # 🌟 3 หมวดหมู่หลักตามปุ่มเลือก
    path('glassware/', views.glassware_list, name='glassware_list'),
    path('instruments/', views.instrument_list, name='instrument_list'),
    path('quiz-40/', views.quiz_40, name='quiz_40'),
    
    # หน้ารายละเอียดอุปกรณ์
    path('equipment/<int:pk>/', views.detail, name='detail'),
    
    # หน้าส่งคะแนนแบบทดสอบ
    path('equipment/<int:pk>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # หน้าสมัครสมาชิก
    path('signup/', views.signup, name='signup'),
    
    # หน้าดูคะแนนของตนเอง (สำหรับผู้ใช้ทั่วไป)
    path('my-scores/', views.my_scores, name='my_scores'),
    
    # หน้า Dashboard ดูคะแนนทั้งหมด (สำหรับ Admin)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('', views.home, name='home'),
    path('glassware/', views.glassware_list, name='glassware_list'),
    path('instruments/', views.instrument_list, name='instrument_list'),
    
    # 🌟 เส้นทางแบบทดสอบ 40 ข้อ
    path('quiz-40/', views.quiz_40, name='quiz_40'),
    path('quiz-40/submit/', views.submit_quiz_40, name='submit_quiz_40'),
    path('quiz-40/result/<int:pk>/', views.quiz_40_result, name='quiz_40_result'),

    path('equipment/<int:pk>/', views.detail, name='detail'),
    path('signup/', views.signup, name='signup'),
    path('my-scores/', views.my_scores, name='my_scores'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]