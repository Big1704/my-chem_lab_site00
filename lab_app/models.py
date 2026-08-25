import re
from django.contrib.auth.models import User
from django.db import models


# 1. ตารางเก็บข้อมูลอุปกรณ์วิทยาศาสตร์/เคมี
class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('glassware', 'เครื่องแก้ว (Glassware)'),
        ('instrument', 'เครื่องมือวิทยาศาสตร์ (Instruments)'),
    ]

    name = models.CharField(max_length=200, verbose_name='ชื่ออุปกรณ์')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='glassware',
        verbose_name='หมวดหมู่อุปกรณ์',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='หน้าที่การทำงาน (เอาไว้ทำอะไร)',
    )
    how_to_use = models.TextField(
        blank=True, null=True, verbose_name='วิธีการใช้งาน'
    )
    cleaning = models.TextField(
        blank=True, null=True, verbose_name='วิธีการเก็บรักษา'
    )
    image = models.ImageField(
        upload_to='equipment/',
        blank=True,
        null=True,
        verbose_name='รูปภาพอุปกรณ์',
    )

    # 🎬 เพิ่มฟิลด์รองรับวิดีโอ
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='ลิงก์วิดีโอ (YouTube)',
    )
    video_file = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        verbose_name='อัปโหลดไฟล์วิดีโอ (MP4)',
    )

    class Meta:
        verbose_name = 'อุปกรณ์ทดลอง'
        verbose_name_plural = 'อุปกรณ์ทดลองทั้งหมด'

    def __str__(self):
        return f'[{self.get_category_display()}] {self.name}'

    # 🛠️ ฟังก์ชันแปลง URL ของ YouTube ให้เป็นลิงก์สำหรับ Embed อัตโนมัติ (ปรับปรุงให้รองรับทุกรูปแบบ)
    @property
    def youtube_embed_url(self):
        if not self.video_url:
            return ''

        # ดึง Video ID ความยาว 11 ตัวอักษร จากรูปแบบ URL ของ YouTube ต่างๆ
        pattern = r'(?:v=|\/embed\/|youtu\.be\/|\/v\/|\/e\/|watch\?v=|\&v=|\/shorts\/)([^#\&\?]{11})'
        match = re.search(pattern, self.video_url)

        if match:
            return f'https://www.youtube.com/embed/{match.group(1)}'

        return self.video_url


# 2. ตารางเก็บข้อมูลผู้ใช้งานและคะแนนการทำแบบทดสอบรายชิ้น
class QuizResult(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='ผู้ใช้งาน'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        verbose_name='อุปกรณ์ที่ทดสอบ',
        null=True,
        blank=True,
    )
    score = models.IntegerField(verbose_name='คะแนนที่ได้')
    date_taken = models.DateTimeField(
        auto_now_add=True, verbose_name='วันที่ทำแบบทดสอบ'
    )

    class Meta:
        verbose_name = 'ผลคะแนนแบบทดสอบ'
        verbose_name_plural = 'ผลคะแนนแบบทดสอบทั้งหมด'

    def __str__(self):
        return f'{self.user.username} ได้ {self.score} คะแนน'


# 3. 🌟 ตารางเก็บผลการสอบแบบทดสอบชุดใหญ่ 40 ข้อ
class Quiz40Result(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='ผู้ใช้งาน'
    )
    score = models.IntegerField(verbose_name='คะแนนที่ได้')
    total_questions = models.IntegerField(
        default=40, verbose_name='จำนวนข้อทั้งหมด'
    )
    percentage = models.FloatField(
        default=0.0, verbose_name='คิดเป็นร้อยละ (%)'
    )
    passed = models.BooleanField(
        default=False, verbose_name='ผลการทดสอบ (ผ่าน 80%)'
    )
    user_answers = models.JSONField(
        default=dict, verbose_name='คำตอบของผู้ใช้'
    )
    date_taken = models.DateTimeField(
        auto_now_add=True, verbose_name='วันที่ทำแบบทดสอบ'
    )

    class Meta:
        verbose_name = 'ผลสอบแบบทดสอบ 40 ข้อ'
        verbose_name_plural = 'ผลสอบแบบทดสอบ 40 ข้อทั้งหมด'

    def __str__(self):
        status = 'ผ่าน' if self.passed else 'ไม่ผ่าน'
        return f'{self.user.username} - ได้ {self.score}/40 คะแนน ({status})'


# 4. 📝 ตารางเก็บผลสอบแบบทดสอบก่อนเรียน (Pre-test)
class QuizPreTestResult(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='ผู้ใช้งาน'
    )
    score = models.IntegerField(verbose_name='คะแนนที่ได้')
    total_questions = models.IntegerField(
        default=40, verbose_name='จำนวนข้อทั้งหมด'
    )
    percentage = models.FloatField(
        default=0.0, verbose_name='คิดเป็นร้อยละ (%)'
    )
    user_answers = models.JSONField(
        default=dict, verbose_name='คำตอบของผู้ใช้'
    )
    date_taken = models.DateTimeField(
        auto_now_add=True, verbose_name='วันที่ทำแบบทดสอบ'
    )

    class Meta:
        verbose_name = 'ผลสอบแบบทดสอบก่อนเรียน'
        verbose_name_plural = 'ผลสอบแบบทดสอบก่อนเรียนทั้งหมด'

    def __str__(self):
        return f'Pre-Test: {self.user.username} - ได้ {self.score}/{self.total_questions} คะแนน'