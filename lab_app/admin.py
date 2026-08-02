from django.contrib import admin
from .models import Equipment, QuizResult, Quiz40Result

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'score', 'date_taken')
    list_filter = ('date_taken',)
    search_fields = ('user__username', 'equipment__name')

# 🌟 เพิ่มการตั้งค่าสำหรับผลสอบ 40 ข้อ
@admin.register(Quiz40Result)
class Quiz40ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'score', 'percentage', 'passed_status', 'date_taken')
    list_filter = ('passed', 'date_taken')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('date_taken', 'user_answers')

    @admin.display(description='ชื่อ-นามสกุล')
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else "-"

    @admin.display(description='ผลการสอบ')
    def passed_status(self, obj):
        return "✅ ผ่าน" if obj.passed else "❌ ไม่ผ่าน"