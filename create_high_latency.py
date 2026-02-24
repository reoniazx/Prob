import csv
import random
from datetime import datetime, timedelta

# ==========================================
# ตั้งค่าพารามิเตอร์
# ==========================================
num_records = 1000             # จำนวนแถวข้อมูลที่ต้องการ
output_file = "high_latency_data.csv" # ชื่อไฟล์ที่ต้องการบันทึก
min_latency = 30
max_latency = 1500

# ความน่าจะเป็นของ Packet Loss (0, 1, 2, 3) 
# ต้องมีค่านี้เพื่อให้ไฟล์นำไปใช้วิเคราะห์ต่อได้
loss_values = [0, 1, 2, 3]
loss_weights = [0.60, 0.25, 0.10, 0.05]

# ==========================================
# เริ่มการสร้างและเขียนไฟล์ CSV
# ==========================================
print(f"กำลังสร้างข้อมูล {num_records} แถว...")

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # เขียน Header ของคอลัมน์ (เพิ่มคอลัมน์ packet_loss แล้ว ✅)
    writer.writerow(["timestamp", "latency_ms", "packet_loss"])
    
    # ตั้งค่าเวลาเริ่มต้น
    start_time = datetime.now()
    
    for i in range(num_records):
        # สร้างเวลาจำลอง (สมมติว่าบันทึก log ทุกๆ 1 วินาที)
        current_time = start_time + timedelta(seconds=i)
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # --- วิธีที่ 2: สุ่มแบบระฆังคว่ำ (Normal Distribution) ---
        # สมมติให้ค่าเฉลี่ยอยู่ที่ 100ms และแกว่ง +- 25ms
        latency_raw = random.gauss(100, 25) 
        
        # ตัดค่าให้อยู่ในกรอบ 30 ถึง 1500 ms เสมอ และปัดเป็นจำนวนเต็ม
        latency = int(max(min_latency, min(latency_raw, max_latency)))
        
        # สุ่ม Packet Loss 
        packet_loss = random.choices(loss_values, weights=loss_weights, k=1)[0]
        
        # เขียนลงไฟล์ทั้ง 3 ค่า
        writer.writerow([timestamp_str, latency, packet_loss])

print(f"✅ สร้างไฟล์ '{output_file}' สำเร็จเรียบร้อยแล้ว!")