import math


# =========================================
# Core Logistic
# =========================================
def logistic(x):
    return 1 / (1 + math.exp(-x))


# =========================================
# Confidence Score
# =========================================
def confidence_score(visit):
    fields = [
        visit.systolic_bp,
        visit.diastolic_bp,
        visit.fasting_glucose,
        visit.bmi,
        visit.smoking,
        visit.family_history
    ]
    known = sum(1 for f in fields if f not in [None, "", 0])
    return round(known / len(fields), 2)


# =========================================
# Generic Risk Builder
# =========================================
def build_risk(name, base, factors):

    total = base + sum(factors.values())
    prob = round(logistic(total) * 100, 1)

    total_abs = sum(abs(v) for v in factors.values()) or 1

    shap = []
    for k, v in factors.items():
        shap.append({
            "feature": k,
            "impact": round((v / total_abs) * 100, 1)
        })

    shap = sorted(shap, key=lambda x: abs(x["impact"]), reverse=True)

    level = (
        "สูงมาก" if prob > 80 else
        "สูง" if prob > 60 else
        "ปานกลาง" if prob > 40 else
        "ต่ำ"
    )

    return {
        "name": name,
        "percent": prob,
        "level": level,
        "shap": shap,
        "main_cause": shap[0]["feature"] if shap else "ไม่มีข้อมูลเด่น"
    }


# =========================================
# MAIN ANALYSIS FUNCTION
# =========================================
def analyze_risk(visit):

    diseases = []

    # 1 CVD
    diseases.append(build_risk(
        "โรคหัวใจและหลอดเลือด", -7,
        {
            "ความดัน": 0.04 * (visit.systolic_bp or 120),
            "น้ำตาล": 0.03 * (visit.fasting_glucose or 90),
            "BMI": 0.05 * (visit.bmi or 22),
            "สูบบุหรี่": 1.5 if visit.smoking == "yes" else 0
        }
    ))

    # 2 Stroke
    diseases.append(build_risk(
        "โรคหลอดเลือดสมอง", -6,
        {
            "ความดัน": 0.05 * (visit.systolic_bp or 120),
            "สูบบุหรี่": 1.2 if visit.smoking == "yes" else 0
        }
    ))

    # 3 Diabetes
    diseases.append(build_risk(
        "เบาหวานชนิดที่ 2", -6,
        {
            "น้ำตาล": 0.06 * (visit.fasting_glucose or 90),
            "BMI": 0.05 * (visit.bmi or 22),
            "ประวัติครอบครัว": 1 if visit.family_history == "yes" else 0
        }
    ))

    # 4 Hypertension
    diseases.append(build_risk(
        "ความดันโลหิตสูงเรื้อรัง", -5,
        {
            "ความดัน": 0.06 * (visit.systolic_bp or 120),
            "BMI": 0.03 * (visit.bmi or 22)
        }
    ))

    # 5 CKD
    diseases.append(build_risk(
        "โรคไตเรื้อรัง", -7,
        {
            "น้ำตาล": 0.04 * (visit.fasting_glucose or 90),
            "ความดัน": 0.03 * (visit.systolic_bp or 120)
        }
    ))

    # 6 Dyslipidemia
    diseases.append(build_risk(
        "ไขมันในเลือดสูง", -5,
        {
            "BMI": 0.04 * (visit.bmi or 22),
            "สูบบุหรี่": 1 if visit.smoking == "yes" else 0
        }
    ))

    # 7 Fatty Liver
    diseases.append(build_risk(
        "โรคตับไขมัน", -6,
        {
            "BMI": 0.06 * (visit.bmi or 22),
            "น้ำตาล": 0.02 * (visit.fasting_glucose or 90)
        }
    ))

    # 8 COPD
    diseases.append(build_risk(
        "โรคปอดอุดกั้นเรื้อรัง", -6,
        {
            "สูบบุหรี่": 2 if visit.smoking == "yes" else 0
        }
    ))

    # 9 Severe Obesity
    diseases.append(build_risk(
        "ภาวะอ้วนรุนแรง", -4,
        {
            "BMI": 0.08 * (visit.bmi or 22)
        }
    ))

    # 10 Metabolic Syndrome
    diseases.append(build_risk(
        "Metabolic Syndrome", -6,
        {
            "BMI": 0.05 * (visit.bmi or 22),
            "ความดัน": 0.04 * (visit.systolic_bp or 120),
            "น้ำตาล": 0.04 * (visit.fasting_glucose or 90)
        }
    ))

    # 11 Coronary Artery Disease
    diseases.append(build_risk(
        "โรคหลอดเลือดหัวใจตีบ", -7,
        {
            "ความดัน": 0.04 * (visit.systolic_bp or 120),
            "สูบบุหรี่": 1.3 if visit.smoking == "yes" else 0,
            "BMI": 0.03 * (visit.bmi or 22)
        }
    ))

    # 12 Peripheral Artery Disease
    diseases.append(build_risk(
        "โรคหลอดเลือดส่วนปลายตีบ", -7,
        {
            "สูบบุหรี่": 1.5 if visit.smoking == "yes" else 0,
            "น้ำตาล": 0.03 * (visit.fasting_glucose or 90)
        }
    ))

    diseases = sorted(diseases, key=lambda x: x["percent"], reverse=True)

    # 10-year simulation based on top disease
    base_risk = diseases[0]["percent"]
    improved_risk = max(base_risk - 20, 5)

    simulation = {
        "current": base_risk,
        "after_lifestyle": improved_risk
    }

    # =========================================
    # 12 Lifestyle Recommendations
    # =========================================
    lifestyle = [
        "ควบคุมน้ำหนักให้อยู่ในช่วง BMI 18.5–22.9",
        "ลดอาหารไขมันอิ่มตัวและน้ำตาล",
        "เพิ่มผักผลไม้วันละ 400 กรัม",
        "ออกกำลังกายอย่างน้อย 150 นาที/สัปดาห์",
        "ควบคุมความดันโลหิตให้น้อยกว่า 130/80",
        "เลิกสูบบุหรี่โดยเด็ดขาด",
        "ลดการดื่มแอลกอฮอล์",
        "ตรวจระดับน้ำตาลทุก 3 เดือน",
        "ตรวจไขมันในเลือดปีละ 1 ครั้ง",
        "พักผ่อน 7–8 ชั่วโมงต่อวัน",
        "จัดการความเครียดอย่างเหมาะสม",
        "ติดตามพบแพทย์ตามนัดอย่างสม่ำเสมอ"
    ]

    return {
        "diseases": diseases,
        "top3": diseases[:3],
        "simulation": simulation,
        "confidence": confidence_score(visit),
        "lifestyle": lifestyle
    }