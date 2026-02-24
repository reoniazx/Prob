import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import csv

# ============================================================
# 📥 โหลดข้อมูลจาก CSV
# ============================================================
# csv_filename = "high_latency_data.csv"
csv_filename = "low_latency_data.csv"
latency_data_raw = []
packet_loss_raw = []

try:
    with open(csv_filename, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            latency_data_raw.append(float(row["latency_ms"]))
            packet_loss_raw.append(int(row["packet_loss"]))
            
    print(f"✅ โหลดข้อมูลจาก '{csv_filename}' สำเร็จ จำนวน {len(latency_data_raw)} รายการ")
except FileNotFoundError:
    print(f"❌ ไม่พบไฟล์ '{csv_filename}'")
    print("กรุณาสร้างไฟล์ CSV หรือรันสคริปต์จำลองข้อมูลก่อนครับ")
    exit()

latency_data = np.array(latency_data_raw)
packet_loss_data = np.array(packet_loss_raw)
n_samples = len(latency_data)

# ============================================================
# 🧮 ประมวลผลและคำนวณสถิติ
# ============================================================

# --- 1. สถิติ Latency พื้นฐาน ---
mean_latency = np.mean(latency_data)
std_latency = np.std(latency_data)
median_latency = np.median(latency_data)

# --- 2. สถิติ Packet Loss (PMF & CDF) ---
unique_losses, counts = np.unique(packet_loss_data, return_counts=True)
probabilities = counts / n_samples 

all_possible_losses = np.array([0, 1, 2, 3])
final_probs = np.zeros(len(all_possible_losses))
for i, loss in enumerate(all_possible_losses):
    if loss in unique_losses:
        idx = np.where(unique_losses == loss)[0][0]
        final_probs[i] = probabilities[idx]

cdf_probs = np.cumsum(final_probs) # คำนวณความน่าจะเป็นสะสม (CDF)

mu_packet = np.sum(all_possible_losses * final_probs)
var_packet = np.sum(((all_possible_losses - mu_packet) ** 2) * final_probs)
std_packet = np.sqrt(var_packet)

# --- 3. Sampling Distribution & Confidence Interval (CI) ---
se_latency = std_latency / np.sqrt(n_samples) # Standard Error
ci95_margin = stats.t.ppf(0.975, n_samples-1) * se_latency
ci99_margin = stats.t.ppf(0.995, n_samples-1) * se_latency

ci95_low, ci95_high = mean_latency - ci95_margin, mean_latency + ci95_margin
ci99_low, ci99_high = mean_latency - ci99_margin, mean_latency + ci99_margin

# --- 4. Hypothesis Testing (1-Sample T-Test) ---
# สมมติฐาน: Router เก่า Ping = 120ms. เราอยากพิสูจน์ว่า Router ใหม่เร็วกว่าเดิม (Ping < 120ms)
H0_mean = 120.0
alpha = 0.05
t_stat = (mean_latency - H0_mean) / se_latency
p_value = stats.t.cdf(t_stat, df=n_samples-1) # One-tailed (Left side)

# ============================================================
# 🖨️ พิมพ์ผลลัพธ์ออกหน้าจอ
# ============================================================
print("\n" + "=" * 55)
print("📊 ผลการคำนวณ (จากข้อมูลจริงใน CSV)")
print("=" * 55)

print("\n📦 Packet Loss (PMF & CDF):")
for x, p, c in zip(all_possible_losses, final_probs, cdf_probs):
    bar = "█" * int(p * 30)
    print(f"   P(X={x}) = {p:.4f} | F(x) = {c:.4f}  {bar}")

print("\n⏱️  Latency Descriptive Stats:")
print(f"   Sample Size (n) = {n_samples}")
print(f"   Mean (x̄)        = {mean_latency:.2f} ms")
print(f"   Median          = {median_latency:.2f} ms")
print(f"   Std Dev (s)     = {std_latency:.2f} ms")

print("\n🎯 Inferential Statistics (Estimation & Hypothesis):")
print(f"   Standard Error (SE) = {se_latency:.2f} ms")
print(f"   95% CI: [{ci95_low:.2f} ms, {ci95_high:.2f} ms]")
print(f"   99% CI: [{ci99_low:.2f} ms, {ci99_high:.2f} ms]")
print(f"   H0: μ = {H0_mean} ms | H1: μ < {H0_mean} ms")
print(f"   T-Statistic = {t_stat:.4f} | P-Value = {p_value:.6f}")
if p_value < alpha:
    print("   👉 Decision: Reject H0 (มีความเร็วเพิ่มขึ้นอย่างมีนัยสำคัญทางสถิติ!)")
else:
    print("   👉 Decision: Fail to reject H0 (ไม่พบความแตกต่างที่ชัดเจน)")

# ============================================================
# 📈 สร้าง Graphs (7 กราฟแบบจัดเต็ม)
# ============================================================
fig = plt.figure(figsize=(15, 22))
fig.suptitle(
    "Comprehensive Network Performance Analysis\nDescriptive, Probability & Inferential Statistics",
    fontsize=18,
    fontweight="bold",
    y=0.98,
)

# แบ่ง Grid เป็น 4 แถว 2 คอลัมน์
gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.4, wspace=0.25)

x_limit_max = max(200, latency_data.max() + 10)

# ------------------------------------------------------------
# Graph 1: Latency Histogram (Stage 1)
# ------------------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0])
ax1.hist(latency_data, bins=30, color="steelblue", edgecolor="white", linewidth=0.8)
ax1.axvline(mean_latency, color="red", linestyle="--", linewidth=2, label=f"Mean = {mean_latency:.1f}")
ax1.axvline(median_latency, color="orange", linestyle="--", linewidth=2, label=f"Median = {median_latency:.1f}")
ax1.set_xlim(0, x_limit_max)
ax1.set_xlabel("Latency (ms)", fontsize=11)
ax1.set_ylabel("Frequency", fontsize=11)
ax1.set_title("1. Latency Distribution (Histogram)", fontsize=13, fontweight="bold")
ax1.legend()
ax1.grid(axis="y", alpha=0.3)

# ------------------------------------------------------------
# Graph 2: Boxplot for Outliers (Stage 1)
# ------------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])
box = ax2.boxplot(latency_data, vert=False, patch_artist=True, flierprops=dict(marker='o', color='red', alpha=0.5))
for patch in box['boxes']:
    patch.set_facecolor('lightblue')
ax2.axvline(mean_latency, color="red", linestyle="--", linewidth=1.5, label="Mean")
ax2.set_xlim(0, x_limit_max)
ax2.set_xlabel("Latency (ms)", fontsize=11)
ax2.set_yticks([])
ax2.set_title("2. Outlier Detection (Boxplot)", fontsize=13, fontweight="bold")
ax2.legend()
ax2.grid(axis="x", alpha=0.3)

# ------------------------------------------------------------
# Graph 3: Packet Loss PMF (Stage 2)
# ------------------------------------------------------------
ax3 = fig.add_subplot(gs[1, 0])
max_p = max(final_probs)
colors = ["#E85D04" if p == max_p else "#F48C06" for p in final_probs]
bars = ax3.bar(all_possible_losses, final_probs, color=colors, edgecolor="white", width=0.6)
for bar, prob in zip(bars, final_probs):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{prob:.2f}", ha="center", fontweight="bold")
ax3.set_xlabel("Packet Losses (x)", fontsize=11)
ax3.set_ylabel("Probability P(x)", fontsize=11)
ax3.set_title("3. Packet Loss Probability (PMF)", fontsize=13, fontweight="bold")
ax3.set_xticks(all_possible_losses)
ax3.set_ylim(0, max(0.5, max_p * 1.3))
ax3.grid(axis="y", alpha=0.3)

# ------------------------------------------------------------
# Graph 4: Packet Loss CDF (Stage 2)
# ------------------------------------------------------------
ax4 = fig.add_subplot(gs[1, 1])
ax4.step(all_possible_losses, cdf_probs, where='post', color='darkgreen', linewidth=2.5)
ax4.plot(all_possible_losses, cdf_probs, 'go') # วาดจุด
for x, c in zip(all_possible_losses, cdf_probs):
    ax4.text(x - 0.1, c + 0.03, f"{c:.2f}", color="darkgreen", fontweight="bold")
ax4.set_xlabel("Packet Losses (x)", fontsize=11)
ax4.set_ylabel("Cumulative Probability F(x)", fontsize=11)
ax4.set_title("4. Cumulative Distribution (CDF)", fontsize=13, fontweight="bold")
ax4.set_xticks(all_possible_losses)
ax4.set_ylim(0, 1.1)
ax4.grid(alpha=0.3)

# ------------------------------------------------------------
# Graph 5: Latency PDF - Normal Approx (Stage 2)
# ------------------------------------------------------------
ax5 = fig.add_subplot(gs[2, 0])
x_pdf = np.linspace(latency_data.min() - std_latency, latency_data.max() + std_latency, 300)
pdf_vals = stats.norm.pdf(x_pdf, mean_latency, std_latency)
ax5.fill_between(x_pdf, pdf_vals, alpha=0.4, color="salmon")
ax5.plot(x_pdf, pdf_vals, color="darkred", linewidth=2)
ax5.axvline(mean_latency, color="black", linestyle="-", label="Mean")
ax5.set_xlim(0, x_limit_max)
ax5.set_xlabel("Latency (ms)", fontsize=11)
ax5.set_ylabel("Density", fontsize=11)
ax5.set_title("5. Population Distribution (PDF)", fontsize=13, fontweight="bold")
ax5.legend()
ax5.grid(axis="y", alpha=0.3)

# ------------------------------------------------------------
# Graph 6: Confidence Intervals & Sampling Dist. (Stage 3)
# ------------------------------------------------------------
ax6 = fig.add_subplot(gs[2, 1])
x_ci = np.linspace(mean_latency - 4*se_latency, mean_latency + 4*se_latency, 300)
samp_dist = stats.t.pdf(x_ci, df=n_samples-1, loc=mean_latency, scale=se_latency)

ax6.plot(x_ci, samp_dist, color="purple", linewidth=2)
# แรเงา 95% CI
x_95 = x_ci[(x_ci >= ci95_low) & (x_ci <= ci95_high)]
ax6.fill_between(x_95, stats.t.pdf(x_95, df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="blue", label="95% CI")
# แรเงา 99% CI (ส่วนที่เลย 95% ออกไป)
x_99_left = x_ci[(x_ci >= ci99_low) & (x_ci < ci95_low)]
x_99_right = x_ci[(x_ci <= ci99_high) & (x_ci > ci95_high)]
ax6.fill_between(x_99_left, stats.t.pdf(x_99_left, df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="orange", label="99% CI Extra")
ax6.fill_between(x_99_right, stats.t.pdf(x_99_right, df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="orange")

ax6.axvline(mean_latency, color="black", linestyle="--")
ax6.set_xlabel("Sample Mean Latency (ms)", fontsize=11)
ax6.set_yticks([])
ax6.set_title("6. Sampling Distribution & C.I.", fontsize=13, fontweight="bold")
ax6.legend(loc="upper right")

# ------------------------------------------------------------
# Graph 7: Hypothesis Testing - T-Test (Stage 4)
# ------------------------------------------------------------
ax7 = fig.add_subplot(gs[3, :]) # ให้ครอบคลุมทั้ง 2 คอลัมน์ด้านล่างสุด
x_hyp = np.linspace(H0_mean - 5*se_latency, H0_mean + 5*se_latency, 400)
null_dist = stats.t.pdf(x_hyp, df=n_samples-1, loc=H0_mean, scale=se_latency)

ax7.plot(x_hyp, null_dist, color="black", linewidth=2, label="H0 Distribution (Router เดิม)")

# หาจุดวิกฤต (Critical Value) ที่ alpha = 0.05 ทางซ้าย
t_crit = stats.t.ppf(alpha, n_samples-1)
x_crit = H0_mean + t_crit * se_latency

# แรเงาพื้นที่ปฏิเสธสมมติฐาน (Rejection Region)
x_reject = x_hyp[x_hyp <= x_crit]
ax7.fill_between(x_reject, stats.t.pdf(x_reject, df=n_samples-1, loc=H0_mean, scale=se_latency), color="red", alpha=0.5, label=f"Rejection Region (α={alpha})")

# ลากเส้นค่าเฉลี่ยที่เราวัดได้จริง
ax7.axvline(mean_latency, color="green", linestyle="--", linewidth=2.5, label=f"Observed Mean ({mean_latency:.1f} ms)")
ax7.axvline(H0_mean, color="black", linestyle=":", linewidth=1.5)

ax7.set_xlabel("Latency (ms)", fontsize=12)
ax7.set_yticks([])
ax7.set_title(f"7. Hypothesis Testing (H0: μ = {H0_mean} ms vs H1: μ < {H0_mean} ms)", fontsize=13, fontweight="bold")
ax7.legend(fontsize=11)

# เซฟและแสดงผล
plt.savefig("network_full_presentation.png", dpi=150, facecolor="white", bbox_inches="tight")
plt.show()
print("\n✅ บันทึกกราฟเป็น: network_full_presentation.png")