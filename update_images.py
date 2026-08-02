import os
import django
import requests
from django.core.files.base import ContentFile

# ตั้งค่า Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chem_lab_site.settings')
django.setup()

from lab_app.models import Equipment

def update_equipment_images():
    print("⏳ กำลังค้นหาและอัปเดตรูปภาพจริงตรงตามชื่ออุปกรณ์...")
    
    items = Equipment.objects.all()
    headers = {'User-Agent': 'ChemLabApp/1.0 (Educational Project)'}

    for idx, item in enumerate(items, 1):
        # ดึงเฉพาะชื่อภาษาอังกฤษ เช่น 'Beaker' จาก 'Beaker (บีกเกอร์)'
        english_name = item.name.split('(')[0].strip()
        
        # ค้นหารูปภาพตรงตามชื่อจาก Wikipedia / Wikimedia Commons
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={english_name}%20glassware&gsrlimit=1&prop=pageimages&piprop=thumbnail&pithumbsize=600&format=json"
        
        img_url = None
        try:
            res = requests.get(search_url, headers=headers, timeout=5).json()
            pages = res.get('query', {}).get('pages', {})
            for p in pages.values():
                if 'thumbnail' in p:
                    img_url = p['thumbnail']['source']
                    break
        except Exception:
            pass

        # หากหาใน Wikimedia ไม่เจอ ให้ใช้รูปตัวอย่างจำลองที่ไม่ซ้ำกัน (ตาม ID)
        if not img_url:
            img_url = f"https://picsum.photos/seed/{item.id}/600/400"

        # โหลดรูปภาพและบันทึกทับรูปเดิมใน Django
        try:
            img_res = requests.get(img_url, headers=headers, timeout=10)
            if img_res.status_code == 200:
                filename = f"equipment_{item.id}.jpg"
                item.image.save(filename, ContentFile(img_res.content), save=True)
                print(f"[{idx}/{len(items)}] ✅ อัปเดตรูปสำเร็จ: {item.name}")
        except Exception as e:
            print(f"[{idx}/{len(items)}] ⚠️ ไม่สามารถโหลดรูปของ {item.name} ได้: {e}")

    print("\n🎉 อัปเดตรูปภาพอุปกรณ์ทั้งหมดเรียบร้อยแล้ว!")

if __name__ == '__main__':
    update_equipment_images()