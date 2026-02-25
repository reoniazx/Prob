import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import csv

# ============================================================
# 📥 โหลดข้อมูลจาก CSV
# ============================================================
csv_filename = "high_latency_data.csv"
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
    exit()

latency_data     = np.array(latency_data_raw)
packet_loss_data = np.array(packet_loss_raw)
n_samples        = len(latency_data)

# ============================================================
# 🧮 ประมวลผลและคำนวณสถิติ
# ============================================================

# --- 1. Latency Stats ---
mean_latency   = np.mean(latency_data)
std_latency    = np.std(latency_data)
median_latency = np.median(latency_data)
q1             = np.percentile(latency_data, 25)
q3             = np.percentile(latency_data, 75)
iqr            = q3 - q1
lower_fence    = q1 - 1.5 * iqr
upper_fence    = q3 + 1.5 * iqr
outliers       = latency_data[(latency_data < lower_fence) | (latency_data > upper_fence)]

# --- 2. Packet Loss PMF & CDF ---
unique_losses, counts = np.unique(packet_loss_data, return_counts=True)
probabilities         = counts / n_samples
all_possible_losses   = np.array([0, 1, 2, 3])
final_probs           = np.zeros(len(all_possible_losses))
for i, loss in enumerate(all_possible_losses):
    if loss in unique_losses:
        idx = np.where(unique_losses == loss)[0][0]
        final_probs[i] = probabilities[idx]

cdf_probs  = np.cumsum(final_probs)
mu_packet  = np.sum(all_possible_losses * final_probs)
var_packet = np.sum(((all_possible_losses - mu_packet) ** 2) * final_probs)
std_packet = np.sqrt(var_packet)

# --- 3. Confidence Interval ---
se_latency   = std_latency / np.sqrt(n_samples)
ci95_margin  = stats.t.ppf(0.975, n_samples - 1) * se_latency
ci99_margin  = stats.t.ppf(0.995, n_samples - 1) * se_latency
ci95_low,  ci95_high = mean_latency - ci95_margin,  mean_latency + ci95_margin
ci99_low,  ci99_high = mean_latency - ci99_margin,  mean_latency + ci99_margin

# --- 4. Hypothesis Testing ---
H0_mean = 120.0
alpha   = 0.05
t_stat  = (mean_latency - H0_mean) / se_latency
p_value = stats.t.cdf(t_stat, df=n_samples - 1)
t_crit  = stats.t.ppf(alpha, n_samples - 1)

# ============================================================
# 🖨️ พิมพ์ผลลัพธ์ทุกกราฟออก Terminal
# ============================================================

DIVIDER = "=" * 60
SUBDIV  = "-" * 60

print("\n" + DIVIDER)
print("  📊 Comprehensive Network Performance Analysis")
print("  Descriptive, Probability & Inferential Statistics")
print(DIVIDER)

# ── Graph 1: Latency Histogram ──────────────────────────────
print("\n📈 [Graph 1] Latency Distribution (Histogram)")
print(SUBDIV)
print(f"  Sample Size (n)  = {n_samples}")
print(f"  Mean (x̄)         = {mean_latency:.4f} ms")
print(f"  Median           = {median_latency:.4f} ms")
print(f"  Std Dev (s)      = {std_latency:.4f} ms")
print(f"  Min              = {latency_data.min():.4f} ms")
print(f"  Max              = {latency_data.max():.4f} ms")
print(f"  Range            = {latency_data.max() - latency_data.min():.4f} ms")
skewness = stats.skew(latency_data)
kurtosis = stats.kurtosis(latency_data)
print(f"  Skewness         = {skewness:.4f}  {'(เบ้ขวา)' if skewness > 0 else '(เบ้ซ้าย)' if skewness < 0 else '(สมมาตร)'}")
print(f"  Kurtosis         = {kurtosis:.4f}  {'(ยอดแหลม)' if kurtosis > 0 else '(ยอดแบน)' if kurtosis < 0 else '(ปกติ)'}")

# ── Graph 2: Boxplot ─────────────────────────────────────────
print("\n📦 [Graph 2] Outlier Detection (Boxplot)")
print(SUBDIV)
print(f"  Q1 (25%)         = {q1:.4f} ms")
print(f"  Q2 / Median      = {median_latency:.4f} ms")
print(f"  Q3 (75%)         = {q3:.4f} ms")
print(f"  IQR (Q3 - Q1)    = {iqr:.4f} ms")
print(f"  Lower Fence      = {lower_fence:.4f} ms  (Q1 - 1.5×IQR)")
print(f"  Upper Fence      = {upper_fence:.4f} ms  (Q3 + 1.5×IQR)")
print(f"  Outliers พบ      = {len(outliers)} ค่า", end="")
if len(outliers) > 0:
    print(f"  → {np.round(outliers, 2).tolist()}")
else:
    print("  → ไม่มี Outlier")

# ── Graph 3: PMF ─────────────────────────────────────────────
print("\n🎲 [Graph 3] Packet Loss Probability (PMF)")
print(SUBDIV)
for x, p in zip(all_possible_losses, final_probs):
    bar = "█" * int(p * 40)
    print(f"  P(X = {x}) = {p:.4f}  {bar}")
print(f"\n  μ  (Mean)        = Σ[x·P(x)]")
for x, p in zip(all_possible_losses, final_probs):
    print(f"                     + ({x} × {p:.4f})")
print(f"                   = {mu_packet:.4f} packet losses/sec")
print(f"  σ² (Variance)    = {var_packet:.4f}")
print(f"  σ  (Std Dev)     = {std_packet:.4f}")

# ── Graph 4: CDF ─────────────────────────────────────────────
print("\n📊 [Graph 4] Cumulative Distribution (CDF)")
print(SUBDIV)
for x, p, c in zip(all_possible_losses, final_probs, cdf_probs):
    bar = "█" * int(c * 40)
    print(f"  F({x}) = P(X ≤ {x}) = {c:.4f}  {bar}")
print(f"\n  แปลผล:")
print(f"  → โอกาส Packet Loss ≤ 0 = {cdf_probs[0]*100:.1f}%")
print(f"  → โอกาส Packet Loss ≤ 1 = {cdf_probs[1]*100:.1f}%")
print(f"  → โอกาส Packet Loss ≤ 2 = {cdf_probs[2]*100:.1f}%")
print(f"  → โอกาส Packet Loss ≤ 3 = {cdf_probs[3]*100:.1f}%")

# ── Graph 5: PDF ─────────────────────────────────────────────
print("\n📉 [Graph 5] Population Distribution (PDF)")
print(SUBDIV)
area_1sigma = stats.norm.cdf(1) - stats.norm.cdf(-1)
area_2sigma = stats.norm.cdf(2) - stats.norm.cdf(-2)
area_3sigma = stats.norm.cdf(3) - stats.norm.cdf(-3)
print(f"  Distribution     : Normal (μ={mean_latency:.2f}, σ={std_latency:.2f})")
print(f"  μ ± 1σ  [{mean_latency - std_latency:.2f}, {mean_latency + std_latency:.2f}] ms → ครอบคลุม {area_1sigma*100:.2f}% ของข้อมูล")
print(f"  μ ± 2σ  [{mean_latency - 2*std_latency:.2f}, {mean_latency + 2*std_latency:.2f}] ms → ครอบคลุม {area_2sigma*100:.2f}% ของข้อมูล")
print(f"  μ ± 3σ  [{mean_latency - 3*std_latency:.2f}, {mean_latency + 3*std_latency:.2f}] ms → ครอบคลุม {area_3sigma*100:.2f}% ของข้อมูล")
prob_above_200 = 1 - stats.norm.cdf(200, mean_latency, std_latency)
print(f"  P(Latency > 200) = {prob_above_200:.4f} ({prob_above_200*100:.2f}%)")

# ── Graph 6: Confidence Interval ─────────────────────────────
print("\n🎯 [Graph 6] Sampling Distribution & Confidence Interval")
print(SUBDIV)
print(f"  Standard Error   = s / √n = {std_latency:.4f} / √{n_samples} = {se_latency:.4f} ms")
print(f"  t-critical (95%) = ±{stats.t.ppf(0.975, n_samples-1):.4f}  (df = {n_samples-1})")
print(f"  t-critical (99%) = ±{stats.t.ppf(0.995, n_samples-1):.4f}  (df = {n_samples-1})")
print(f"  95% CI           = [{ci95_low:.4f}, {ci95_high:.4f}] ms  (±{ci95_margin:.4f})")
print(f"  99% CI           = [{ci99_low:.4f}, {ci99_high:.4f}] ms  (±{ci99_margin:.4f})")
print(f"\n  แปลผล:")
print(f"  → มั่นใจ 95% ว่าค่า Latency จริงอยู่ใน [{ci95_low:.2f}, {ci95_high:.2f}] ms")
print(f"  → มั่นใจ 99% ว่าค่า Latency จริงอยู่ใน [{ci99_low:.2f}, {ci99_high:.2f}] ms")

# ── Graph 7: Hypothesis Testing ──────────────────────────────
print("\n🔬 [Graph 7] Hypothesis Testing (1-Sample T-Test)")
print(SUBDIV)
print(f"  H0 (สมมติฐานหลัก) : μ = {H0_mean} ms  (Router เดิม)")
print(f"  H1 (สมมติฐานแย้ง) : μ < {H0_mean} ms  (Router ใหม่เร็วกว่า)")
print(f"  Significance (α)  = {alpha}")
print(f"\n  T-Statistic       = (x̄ - μ₀) / SE")
print(f"                    = ({mean_latency:.4f} - {H0_mean}) / {se_latency:.4f}")
print(f"                    = {t_stat:.4f}")
print(f"  P-Value           = {p_value:.6f}")
print(f"  T-Critical        = {t_crit:.4f}  (one-tailed left)")
print(f"\n  เงื่อนไขการปฏิเสธ : t_stat < t_crit  หรือ  p_value < α")
print(f"  ผล                : {t_stat:.4f} {'<' if t_stat < t_crit else '≥'} {t_crit:.4f}  |  {p_value:.6f} {'<' if p_value < alpha else '≥'} {alpha}")
if p_value < alpha:
    print(f"\n  👉 Decision: ✅ Reject H0")
    print(f"     Router ใหม่มี Latency ต่ำกว่า {H0_mean} ms อย่างมีนัยสำคัญทางสถิติ")
else:
    print(f"\n  👉 Decision: ❌ Fail to Reject H0")
    print(f"     ไม่พบหลักฐานเพียงพอว่า Router ใหม่เร็วกว่า {H0_mean} ms")

print("\n" + DIVIDER)

# ============================================================
# 📈 สร้าง Graphs
# ============================================================
fig = plt.figure(figsize=(10, 15))
fig.suptitle(
    "Comprehensive Network Performance Analysis\nDescriptive, Probability & Inferential Statistics",
    fontsize=18, fontweight="bold", y=0.98,
)
gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.4, wspace=0.25)
x_limit_max = max(200, latency_data.max() + 10)

# Graph 1
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

# Graph 2
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

# Graph 3
ax3 = fig.add_subplot(gs[1, 0])
max_p  = max(final_probs)
colors = ["#E85D04" if p == max_p else "#F48C06" for p in final_probs]
bars   = ax3.bar(all_possible_losses, final_probs, color=colors, edgecolor="white", width=0.6)
for bar, prob in zip(bars, final_probs):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{prob:.2f}", ha="center", fontweight="bold")
ax3.set_xlabel("Packet Losses (x)", fontsize=11)
ax3.set_ylabel("Probability P(x)", fontsize=11)
ax3.set_title("3. Packet Loss Probability (PMF)", fontsize=13, fontweight="bold")
ax3.set_xticks(all_possible_losses)
ax3.set_ylim(0, max(0.5, max_p * 1.3))
ax3.grid(axis="y", alpha=0.3)

# Graph 4
ax4 = fig.add_subplot(gs[1, 1])
ax4.step(all_possible_losses, cdf_probs, where='post', color='darkgreen', linewidth=2.5)
ax4.plot(all_possible_losses, cdf_probs, 'go')
for x, c in zip(all_possible_losses, cdf_probs):
    ax4.text(x - 0.1, c + 0.03, f"{c:.2f}", color="darkgreen", fontweight="bold")
ax4.set_xlabel("Packet Losses (x)", fontsize=11)
ax4.set_ylabel("Cumulative Probability F(x)", fontsize=11)
ax4.set_title("4. Cumulative Distribution (CDF)", fontsize=13, fontweight="bold")
ax4.set_xticks(all_possible_losses)
ax4.set_ylim(0, 1.1)
ax4.grid(alpha=0.3)

# Graph 5
ax5 = fig.add_subplot(gs[2, 0])
x_pdf    = np.linspace(latency_data.min() - std_latency, latency_data.max() + std_latency, 300)
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

# Graph 6
ax6 = fig.add_subplot(gs[2, 1])
x_ci     = np.linspace(mean_latency - 4*se_latency, mean_latency + 4*se_latency, 300)
samp_dist = stats.t.pdf(x_ci, df=n_samples-1, loc=mean_latency, scale=se_latency)
ax6.plot(x_ci, samp_dist, color="purple", linewidth=2)
x_95 = x_ci[(x_ci >= ci95_low) & (x_ci <= ci95_high)]
ax6.fill_between(x_95, stats.t.pdf(x_95, df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="blue", label="95% CI")
x_99_left  = x_ci[(x_ci >= ci99_low) & (x_ci < ci95_low)]
x_99_right = x_ci[(x_ci <= ci99_high) & (x_ci > ci95_high)]
ax6.fill_between(x_99_left,  stats.t.pdf(x_99_left,  df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="orange", label="99% CI Extra")
ax6.fill_between(x_99_right, stats.t.pdf(x_99_right, df=n_samples-1, loc=mean_latency, scale=se_latency), alpha=0.3, color="orange")
ax6.axvline(mean_latency, color="black", linestyle="--")
ax6.set_xlabel("Sample Mean Latency (ms)", fontsize=11)
ax6.set_yticks([])
ax6.set_title("6. Sampling Distribution & C.I.", fontsize=13, fontweight="bold")
ax6.legend(loc="upper right")

# Graph 7
ax7 = fig.add_subplot(gs[3, :])
x_hyp     = np.linspace(H0_mean - 5*se_latency, H0_mean + 5*se_latency, 400)
null_dist = stats.t.pdf(x_hyp, df=n_samples-1, loc=H0_mean, scale=se_latency)
ax7.plot(x_hyp, null_dist, color="black", linewidth=2, label="H0 Distribution (Router เดิม)")
x_crit_val = H0_mean + t_crit * se_latency
x_reject   = x_hyp[x_hyp <= x_crit_val]
ax7.fill_between(x_reject, stats.t.pdf(x_reject, df=n_samples-1, loc=H0_mean, scale=se_latency), color="red", alpha=0.5, label=f"Rejection Region (α={alpha})")
ax7.axvline(mean_latency, color="green", linestyle="--", linewidth=2.5, label=f"Observed Mean ({mean_latency:.1f} ms)")
ax7.axvline(H0_mean, color="black", linestyle=":", linewidth=1.5)
ax7.set_xlabel("Latency (ms)", fontsize=12)
ax7.set_yticks([])
ax7.set_title(f"7. Hypothesis Testing (H0: μ = {H0_mean} ms vs H1: μ < {H0_mean} ms)", fontsize=13, fontweight="bold")
ax7.legend(fontsize=11)

plt.savefig("high_network_full_presentation.png", dpi=150, facecolor="white", bbox_inches="tight")
plt.show()
print("✅ บันทึกกราฟเป็น: high_network_full_presentation.png")