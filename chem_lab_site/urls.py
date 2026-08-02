"""
URL configuration for chem_lab_site project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # หน้าต่างจัดการระบบหลังบ้านสำหรับ Admin
    path('admin/', admin.site.urls),
    
    # ระบบล็อกอิน/เอาต์สำเร็จรูปของ Django
    path('accounts/', include('django.contrib.auth.urls')),
    
    # ส่งการทำงานไปยัง urls.py ของแอป lab_app
    path('', include('lab_app.urls')),
]

# เปิดให้ระบบดึงรูปภาพจากโฟลเดอร์ media มาแสดงผล
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)