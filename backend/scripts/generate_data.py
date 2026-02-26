"""
Rich synthetic hospital dataset generator.
Produces 18 multi-paragraph reports across 10 departments with:
  - 5 conflict pairs (documents that directly contradict each other)
  - 8 standalone / non-conflicting documents (consistent information)

Each document is 400-1200 words to produce 50-80 meaningful chunks after splitting.
"""
import os
import json
from fpdf import FPDF
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ─── CONFLICT PAIR 1: Patient Satisfaction ────────────────────────────────────
# Report 01 says satisfaction is way up. Report 02 says ER complaints spiked.

DOC_01 = {
    "filename": "01_Patient_Relations_Q1_Survey.pdf",
    "type": "pdf",
    "metadata": {"department": "Patient Relations", "date": "2026-03-31", "source_type": "survey", "author": "Dr. Alice Smith"},
    "content": """*CONFIDENTIAL - Patient Relations Department*
Date: 2026-03-31 | Author: Dr. Alice Smith

QUARTERLY PATIENT SATISFACTION SURVEY — Q1 2026

Executive Summary:
Patient satisfaction has improved by 20% compared to Q4 2025 across all major departments. This improvement is attributed to the comprehensive hospitality training program that was rolled out in January 2026, which 95% of patient-facing staff completed.

Detailed Findings:

1. DISCHARGE SURVEY RESULTS
A total of 3,247 discharge surveys were collected during Q1 2026, representing a 78% response rate (up from 61% in Q4 2025). The overall satisfaction score rose to 4.3 out of 5.0, compared to 3.6 in the previous quarter. The most significant improvements were observed in the categories of "Staff Friendliness" (up 28%), "Communication Clarity" (up 22%), and "Wait Time Perception" (up 15%).

2. DEPARTMENT-SPECIFIC HIGHLIGHTS
The Pediatric Ward received the highest satisfaction scores at 4.7/5.0, with patients and families consistently praising the new play therapy program introduced in February. The Surgical Wing scored 4.4/5.0, with patients noting the excellent pre-operative counseling services. The General Medicine floor improved to 4.1/5.0, up from 3.3 in the prior quarter.

3. COMPLAINT VOLUME ANALYSIS
Total formal complaints decreased from 142 in Q4 2025 to 89 in Q1 2026, a 37% reduction. The most common complaint categories were parking availability (24 complaints), food quality (18 complaints), and billing clarity (15 complaints). Notably, complaints related to staff rudeness dropped by 62%, from 34 to 13 instances.

4. NET PROMOTER SCORE
The hospital's Net Promoter Score (NPS) improved from +12 to +34, placing us in the "Good" category for the first time in three years. 67% of patients rated their experience as 9 or 10 out of 10 on the likelihood-to-recommend scale.

5. RECOMMENDATIONS
Continue the hospitality training program with quarterly refresher sessions. Expand the patient feedback kiosk system to the Radiology and Endoscopy units. Consider implementing real-time satisfaction tracking via mobile app for immediate service recovery opportunities.

Prepared by: Dr. Alice Smith, Director of Patient Experience
Distribution: Hospital Board, Department Heads, Quality Committee"""
}

DOC_02 = {
    "filename": "02_Emergency_Dept_Incident_Log.txt",
    "type": "txt",
    "metadata": {"department": "Emergency", "date": "2026-04-02", "source_type": "log", "author": "Dr. James Rivera"},
    "content": """EMERGENCY DEPARTMENT — Q1 2026 INCIDENT LOG SUMMARY
Compiled by: Dr. James Rivera, ED Medical Director
Date: 2026-04-02

CRITICAL FINDINGS:

1. PATIENT VOLUME & WAIT TIMES
The Emergency Department experienced a 30% surge in patient volume during Q1 2026, with an average of 287 patients per day (up from 221 in Q4 2025). Average wait times increased from 42 minutes to 87 minutes, with peak wait times exceeding 3 hours on 14 occasions during the quarter. This represents a DANGEROUS deterioration in our ability to provide timely emergency care.

2. COMPLAINT STATISTICS
Emergency department complaints rose by 25% in Q1 2026, reaching 178 formal complaints (up from 142 in Q4 2025). The most critical complaint categories were: excessive wait times (72 complaints), perceived staff indifference (38 complaints), inadequate pain management (29 complaints), and lack of communication during wait periods (21 complaints). 23 complaints specifically mentioned patients leaving against medical advice or leaving without being seen (LWBS).

3. LWBS RATE
The Left Without Being Seen (LWBS) rate reached 8.7% in March 2026, far exceeding the national benchmark of 2%. Over the quarter, 247 patients left the Emergency Department without receiving medical evaluation. Three of these patients returned within 24 hours requiring immediate admission, including one patient who suffered a cardiac event at home.

4. STAFFING OBSERVATIONS
Despite HR reports indicating full staffing, the ED regularly operated with only 60-70% of required nursing coverage during night shifts and weekends. Agency nurse utilization was 340 hours in March alone, contradicting claims that agency nurses were unnecessary. Staff burnout indicators are elevated, with 6 ED nurses requesting transfers to other departments.

5. PATIENT SAFETY CONCERNS
Two sentinel events occurred during Q1: (a) a patient with chest pain waited 2.5 hours before triage re-evaluation, and (b) a pediatric patient with a femur fracture was left in the waiting room for 90 minutes without pain management. Both cases are under formal review.

6. RECOMMENDATIONS
Immediate increase in ED staffing levels by a minimum of 4 RNs per shift. Implementation of a rapid triage protocol for high-acuity patients. Installation of a real-time wait time display system. Formal review of the discrepancy between HR staffing reports and actual ED coverage.

SIGNED: Dr. James Rivera, MD, FACEP
Emergency Department Medical Director"""
}

# ─── CONFLICT PAIR 2: MRI Machine Status ─────────────────────────────────────

DOC_03 = {
    "filename": "03_Radiology_Equipment_Update.pdf",
    "type": "pdf",
    "metadata": {"department": "Radiology", "date": "2026-03-15", "source_type": "memo", "author": "Dr. Gregory House"},
    "content": """RADIOLOGY DEPARTMENT — EQUIPMENT STATUS REPORT
Date: 2026-03-15 | Author: Dr. Gregory House, Chief of Radiology

NEW MRI MACHINE — OPERATIONAL STATUS: FULLY OPERATIONAL

The Siemens MAGNETOM Vida 3T MRI system was successfully installed and calibrated on February 28, 2026, passing all safety inspections and receiving certification from the state Department of Health. The machine has been fully operational since March 1, 2026.

PERFORMANCE METRICS:
- Average daily scan volume: 48-52 patients per day
- Average scan duration: 32 minutes (compared to 45 minutes on our old 1.5T unit)
- Image quality ratings: Consistently rated "Excellent" by our radiologists
- Equipment downtime: Zero unplanned downtime since commissioning
- Patient satisfaction with MRI experience: 4.6/5.0

BACKLOG REDUCTION:
The previous MRI waitlist of 847 patients has been reduced to 210 patients as of March 15, a 75% reduction in just two weeks. We project full backlog clearance by April 10 at current throughput rates. Urgent and emergency MRI requests are now being fulfilled within 4 hours of order placement, compared to the previous 24-48 hour wait.

FINANCIAL IMPACT:
The new system has enabled us to eliminate $42,000/month in outsourced MRI referrals to neighboring hospitals. At current utilization rates, the machine is generating approximately $185,000/month in revenue, putting us on track for a return on investment within 18 months, ahead of the projected 24-month timeline.

STAFF TRAINING:
All 8 MRI technologists have completed manufacturer certification on the new system. Three technologists have also completed advanced cardiac MRI training, enabling us to offer cardiac stress MRI for the first time in our hospital's history.

Prepared by: Dr. Gregory House, MD
Chief of Radiology"""
}

DOC_04 = {
    "filename": "04_Facilities_Maintenance_Log.md",
    "type": "md",
    "metadata": {"department": "Facilities", "date": "2026-03-20", "source_type": "record", "author": "Robert Martinez"},
    "content": """# Facilities Management — Equipment Installation Log
**Author:** Robert Martinez, Facilities Director
**Date:** 2026-03-20

## MRI Installation Project — Status: DELAYED / NON-OPERATIONAL

### Current Status
The new MRI machine installation remains incomplete as of March 20, 2026. The system is CURRENTLY NON-OPERATIONAL due to the following unresolved issues:

### Issue 1: Gradient Coil Defect
During the final calibration phase on February 25, the primary gradient coil was found to have a manufacturing defect that produces unacceptable image artifacts at field strengths above 2.0T. The defective component was shipped back to the manufacturer (Siemens Healthcare, Erlangen, Germany) on March 2. We are awaiting a replacement coil, which has an estimated delivery date of April 18-25, 2026.

### Issue 2: RF Shielding Failure
The radiofrequency shielding in Suite MRI-2 failed the electromagnetic compatibility test on March 8. External RF interference from the new cell tower installed on the hospital roof in January 2026 is causing significant image degradation. A specialized RF shielding contractor (MagShield Inc.) has been engaged and is scheduled to complete remediation work by April 5, 2026.

### Issue 3: Helium Supply Chain
The cryogenic helium supply required for the superconducting magnet has been impacted by global supply chain disruptions. Our current helium reserve will last approximately 6 weeks, but we require a guaranteed continuous supply before committing to full operation.

### Patient Impact
All MRI appointments are being redirected to the OLD 1.5T scanner (Siemens Aera), which is currently operating at 130% of its recommended duty cycle. This is causing accelerated wear on the old machine, and we have already experienced two unplanned shutdowns (March 5 and March 12) requiring emergency service calls totaling $8,400.

### Financial Impact
The installation delays have resulted in approximately $127,000 in additional costs including contractor overtime, temporary scanner rental fees, and patient referral costs to external facilities. Additionally, the manufacturer's warranty clock starts ticking upon delivery, meaning we are losing warranty coverage days without operational benefit.

### Projected Timeline
Optimistic: Full operation by May 1, 2026
Realistic: Full operation by May 15, 2026
Pessimistic: Full operation by June 1, 2026

**Signed:** Robert Martinez, Facilities Director"""
}

# ─── CONFLICT PAIR 3: Infection Rates ─────────────────────────────────────────

DOC_05 = {
    "filename": "05_Surgical_Infection_Control_Report.pdf",
    "type": "pdf",
    "metadata": {"department": "Surgical", "date": "2026-02-28", "source_type": "report", "author": "Dr. Miranda Bailey"},
    "content": """SURGICAL DEPARTMENT — INFECTION CONTROL QUARTERLY REPORT
Author: Dr. Miranda Bailey, Chief of Surgery
Period: Q1 2026 (January 1 - March 31)

EXECUTIVE SUMMARY:
The Surgical Wing has achieved a historic milestone with post-surgical infection rates decreasing to an all-time low of 1.2% this quarter. This represents a 60% reduction from Q4 2025 (3.0%) and places us well below the national benchmark of 2.8%.

CONTRIBUTING FACTORS:

1. UV-C STERILIZATION PROTOCOL
The new UV-C robotic sterilization system, deployed in all 12 operating rooms since January 15, 2026, has been the primary driver of our improvement. Each OR undergoes a 15-minute UV-C decontamination cycle between procedures, in addition to standard manual cleaning. Bacterial colony counts on surface swabs have decreased by 94% post-implementation.

2. SURGICAL CHECKLIST COMPLIANCE
WHO Surgical Safety Checklist compliance has reached 99.7% (up from 91% in Q4 2025) following the introduction of mandatory electronic documentation. Non-compliance triggers an automatic alert to the attending surgeon and the Quality Department.

3. ANTIBIOTIC STEWARDSHIP
The revised antibiotic prophylaxis protocol, which standardizes pre-operative antibiotic administration timing to 30-60 minutes before incision, has achieved 96% compliance. Studies from our pharmacy department confirm a correlation between protocol compliance and reduced surgical site infections (SSIs).

4. HAND HYGIENE MONITORING
Electronic hand hygiene monitoring badges, worn by all surgical staff, have increased hand hygiene compliance from 78% to 97%. The system provides real-time alerts when staff approach a patient without performing hand hygiene.

DETAILED STATISTICS:
- Total surgical procedures Q1: 2,847
- Post-surgical infections identified: 34 (1.2%)
- Breakdown by procedure type:
  * Orthopedic: 0.8% (8 infections / 1,023 procedures)
  * General Surgery: 1.4% (12 infections / 857 procedures)
  * Cardiac: 1.1% (6 infections / 545 procedures)
  * Neurosurgery: 1.9% (8 infections / 422 procedures)

Prepared by: Dr. Miranda Bailey, MD, FACS
Chief of Surgery"""
}

DOC_06 = {
    "filename": "06_ICU_Infection_Alert.txt",
    "type": "txt",
    "metadata": {"department": "ICU", "date": "2026-03-05", "source_type": "alert", "author": "Charge Nurse Patricia Kelly"},
    "content": """URGENT PATIENT SAFETY ALERT — ICU INFECTION OUTBREAK
Classification: CRITICAL
Date: 2026-03-05
Author: Charge Nurse Patricia Kelly, MSN, RN-BC

ALERT SUMMARY:
The Intensive Care Unit is reporting a significant and alarming spike in hospital-acquired infections (HAIs) during Q1 2026. The overall HAI rate in the ICU has reached 4.5% this quarter, representing a 180% increase from Q4 2025 (1.6%) and far exceeding the national ICU benchmark of 2.1%.

INFECTION BREAKDOWN:
1. Central Line-Associated Bloodstream Infections (CLABSI): 12 cases (rate: 3.2 per 1,000 catheter days, national benchmark: 0.8)
2. Catheter-Associated Urinary Tract Infections (CAUTI): 8 cases (rate: 2.1 per 1,000 catheter days, national benchmark: 0.9)
3. Ventilator-Associated Pneumonia (VAP): 6 cases (rate: 1.8 per 1,000 ventilator days, national benchmark: 0.9)
4. Surgical Site Infections (transferred surgical patients): 4 cases
5. C. difficile infections: 3 cases

ROOT CAUSE ANALYSIS — PRELIMINARY FINDINGS:

Factor 1: STERILIZATION EQUIPMENT FAILURE
The UV-C sterilization unit assigned to the ICU (Unit #3) has been malfunctioning intermittently since January 22, 2026. Maintenance logs show it was flagged for repair on January 28, but the work order was not completed until February 15 — a gap of 18 days during which the ICU relied solely on manual cleaning protocols.

Factor 2: STAFFING-DRIVEN PROTOCOL LAPSES
Due to chronic understaffing during night shifts, hand hygiene compliance in the ICU dropped to 64% (monitored by electronic badges), compared to 92% during day shifts. Central line bundle compliance also fell to 71% during nights, versus 95% during days.

Factor 3: PATIENT ACUITY
Average patient acuity scores increased by 18% this quarter, with a higher proportion of immunocompromised patients (oncology referrals increased 40%). Higher acuity patients are inherently more susceptible to HAIs.

IMMEDIATE ACTIONS TAKEN:
- UV-C Unit #3 replaced with a backup unit on February 16
- Mandatory hand hygiene re-training completed for all ICU staff (February 20-22)
- Temporary 1:1 nursing ratio implemented for all central line patients
- Environmental cultures obtained from all ICU surfaces and equipment

PATIENT OUTCOMES:
Of the 33 HAI cases: 2 patients died (both with multiple comorbidities), 7 required extended ICU stays averaging 8.4 additional days, and estimated additional treatment costs total approximately $412,000.

FORMAL REQUEST:
This alert constitutes a formal request for an immediate hospital-wide infection control audit and additional ICU nursing FTEs.

Signed: Patricia Kelly, MSN, RN-BC
ICU Charge Nurse & Infection Prevention Liaison"""
}

# ─── CONFLICT PAIR 4: Staffing Levels ─────────────────────────────────────────

DOC_07 = {
    "filename": "07_HR_Staffing_Briefing.pdf",
    "type": "pdf",
    "metadata": {"department": "HR", "date": "2026-01-15", "source_type": "briefing", "author": "Tom Henderson"},
    "content": """HUMAN RESOURCES — Q1 STAFFING REPORT
Date: 2026-01-15 | Author: Tom Henderson, VP of Human Resources

STAFFING STATUS: FULLY STAFFED — ALL POSITIONS FILLED

EXECUTIVE SUMMARY:
Our comprehensive hiring campaign launched in October 2025 has been an outstanding success. As of January 15, 2026, nursing staff levels are at 100% capacity across all shifts and all departments. We have eliminated the need for agency/travel nurses entirely, resulting in projected savings of $1.2 million annually.

RECRUITMENT RESULTS:
- Total new hires: 67 registered nurses, 23 licensed practical nurses, 12 nursing assistants
- Positions filled: 102 of 102 budgeted positions (100%)
- Average time-to-fill: 28 days (industry average: 49 days)
- Offer acceptance rate: 89% (industry average: 72%)

RETENTION IMPROVEMENTS:
New retention initiatives have reduced turnover to 8.2% annualized, compared to the industry average of 18.4%. Key initiatives include:
- Sign-on bonuses of $5,000-$15,000 depending on specialty
- Tuition reimbursement program (84 nurses enrolled)
- Flexible scheduling options adopted by 71% of nursing staff
- New mentorship program pairing experienced nurses with new hires

SHIFT COVERAGE ANALYSIS:
All units report adequate coverage for all three shifts:
- Day shift (7a-3p): 100% coverage, 0 open positions
- Evening shift (3p-11p): 100% coverage, 0 open positions
- Night shift (11p-7a): 100% coverage, 0 open positions
- Weekend coverage: 100% through the new weekend warrior premium pay program

We do not anticipate needing agency nurses at any point during Q1 2026.

CONCLUSION:
This is the first time in 4 years that the hospital has achieved full nursing staff capacity. This achievement reflects the effectiveness of our new compensation packages and work-life balance initiatives.

Prepared by: Tom Henderson
VP of Human Resources"""
}

DOC_08 = {
    "filename": "08_NightShift_Supervisor_Log.md",
    "type": "md",
    "metadata": {"department": "General Wards", "date": "2026-02-10", "source_type": "log", "author": "Sarah Chen"},
    "content": """# Night Shift Supervisor Log — Multiple Entries
**Author:** Sarah Chen, Night Shift Supervisor
**Dates:** January 15 - March 15, 2026

## January 15, 2026 — CRITICAL STAFFING SHORTAGE
Night shift began with only 12 of 19 required nursing staff present. Three nurses called in sick, two positions remain unfilled despite HR's claim of 100% staffing, and two nurses were pulled to cover the Emergency Department. Mandatory overtime was initiated for 5 staff members from the evening shift, resulting in 16-hour shifts for these individuals.

Ward 3B operated with a nurse-to-patient ratio of 1:9, well above the safe threshold of 1:5 for acute medical patients. One medication error occurred (wrong dose of heparin) that was caught by pharmacy before administration.

## January 28, 2026 — RESIGNATION CLUSTER
Three experienced night shift nurses (combined 34 years of experience) submitted resignation notices today, effective February 28. All three cited unsustainable workload, mandatory overtime, and concerns about patient safety as their primary reasons for leaving. This will increase our staffing deficit to 5 unfilled positions on nights.

## February 10, 2026 — UNSAFE CONDITIONS
Severe nursing shortages again tonight. 11 of 19 positions staffed. Called the nursing supervisor for help; was told no agency nurses are authorized per HR directive. Two patient falls occurred on Ward 2A (one resulting in a hip fracture requiring surgical intervention). Contributing factor was inadequate rounding due to staffing levels.

Staff morale is critically low. The break room whiteboard has been filled with anonymous complaints about workload and management's disconnect from floor conditions. I have filed a formal safe harbor declaration for tonight's shift.

## February 25, 2026 — CONTINUED DETERIORATION
Mandatory overtime has been required on 18 of 25 night shifts this month. Three more nurses have begun interviewing at competing hospitals. The ward clerk reported overhearing multiple nurses discussing "quiet quitting" — doing the minimum required rather than going above and beyond.

## March 15, 2026 — FORMAL COMPLAINT
I am formally documenting that night shift staffing levels have been critically unsafe for the majority of Q1 2026. Despite repeated escalations to HR and nursing administration, conditions have not improved. The claim that we are "100% staffed" does not reflect the reality on the floor. I am requesting that this log be entered into the official quality and safety record.

**Signed:** Sarah Chen, BSN, RN
Night Shift Supervisor, General Medical Wards"""
}

# ─── CONFLICT PAIR 5: Financial / Overtime Costs ──────────────────────────────

DOC_09 = {
    "filename": "09_Finance_Q1_Summary.pdf",
    "type": "pdf",
    "metadata": {"department": "Finance", "date": "2026-03-31", "source_type": "report", "author": "Angela Chen"},
    "content": """FINANCE DEPARTMENT — Q1 2026 FINANCIAL SUMMARY
Date: 2026-03-31 | Author: Angela Chen, CFO

EXECUTIVE SUMMARY:
Hospital operating costs decreased by 10% in Q1 2026, totaling $47.2 million compared to $52.4 million in Q4 2025. This represents the most significant quarterly cost reduction in the hospital's recent history and reflects the success of multiple operational efficiency initiatives.

KEY SAVINGS AREAS:

1. LABOR COSTS: Down 12% ($2.1M saved)
Elimination of agency nurse contracts saved approximately $1.2 million. Overtime pay was reduced by $540,000 through improved scheduling and hiring. Benefits costs declined by $360,000 due to a renegotiated insurance contract.

2. SUPPLY CHAIN: Down 8% ($890K saved)
Group purchasing organization (GPO) renegotiations secured better pricing on surgical supplies, pharmaceuticals, and medical devices. Introduction of par-level inventory management reduced waste and expiration losses by 35%.

3. ENERGY COSTS: Down 15% ($420K saved)
The new building management system, installed in December 2025, has optimized HVAC, lighting, and equipment scheduling. LED lighting retrofits in administrative areas contributed an additional $85,000 in annual savings.

4. REVENUE PERFORMANCE: Up 5%
Patient revenue increased to $58.3 million, driven by higher surgical volumes and the new MRI service line. Payer mix improved slightly with a 2% increase in commercially insured patients.

PROFITABILITY:
Operating margin improved from 2.1% in Q4 2025 to 7.8% in Q1 2026, exceeding our annual target of 5%.

Prepared by: Angela Chen, MBA, CPA
Chief Financial Officer"""
}

DOC_10 = {
    "filename": "10_Union_Grievance_Filing.txt",
    "type": "txt",
    "metadata": {"department": "Labor Relations", "date": "2026-03-25", "source_type": "grievance", "author": "Marcus Johnson"},
    "content": """NURSES UNION LOCAL 1199 — FORMAL GRIEVANCE
Grievance Number: 2026-GR-0442
Date Filed: March 25, 2026
Filed By: Marcus Johnson, Union Representative

SUBJECT: Excessive Mandatory Overtime, Unsafe Working Conditions, and Misrepresentation of Staffing Data

STATEMENT OF GRIEVANCE:

The Nurses Union formally grieves that hospital management has violated Articles 7 (Hours of Work), 12 (Health and Safety), and 15 (Good Faith) of the current Collective Bargaining Agreement (CBA) through systematic understaffing, excessive mandatory overtime, and public misrepresentation of staffing adequacy.

FACTUAL BASIS:

1. OVERTIME DATA (sourced from payroll records obtained via FOIA request):
Total overtime hours worked by nursing staff in Q1 2026: 14,847 hours. This represents a 94% increase from Q4 2025 (7,650 hours) and contradicts management's public claims that overtime has been "reduced." Mandatory overtime was invoked on 67% of night shifts during the quarter.

2. OVERTIME PAY DISCREPANCY:
Payroll records show $1,847,000 in overtime wages paid during Q1 2026. This DIRECTLY CONTRADICTS the Finance Department's claim of a $540,000 REDUCTION in overtime pay. The union's independent analysis suggests the Finance report may have incorrectly categorized overtime pay under different budget line items or excluded mandatory overtime from the "scheduled overtime" category being reported.

3. AGENCY NURSE UTILIZATION:
Despite HR's assertion that agency nurses were eliminated, payroll records show $287,000 in payments to three staffing agencies during Q1 2026: NurseFlex ($142,000), StaffBridge ($98,000), and MedTemp ($47,000). These payments were coded under "Contracted Services" rather than "Agency Nursing," obscuring the true expenditure.

4. UNSAFE NURSE-TO-PATIENT RATIOS:
Union shift reports document 43 instances of nurse-to-patient ratios exceeding safe limits during Q1 2026. On 12 occasions, ratios exceeded 1:8 on acute medical floors (safe limit: 1:5). These incidents correlate with the documented increase in patient falls and medication errors.

RELIEF REQUESTED:
1. Immediate hiring of 25 additional RN positions
2. Restriction of mandatory overtime to genuine emergencies only
3. Independent audit of staffing hours and overtime pay reporting
4. $450,000 in retroactive hazard pay for nurses who worked unsafe shifts
5. Corrective disclosure of accurate staffing and financial data to the hospital board

Signed: Marcus Johnson, BSN, RN
Union Representative, Nurses Union Local 1199"""
}

# ─── NON-CONFLICT DOCUMENTS ──────────────────────────────────────────────────
# These documents cover standalone topics or are consistent with other data.

DOC_11 = {
    "filename": "11_Lab_Turnaround_Improvement.pdf",
    "type": "pdf",
    "metadata": {"department": "Laboratory", "date": "2026-03-10", "source_type": "report", "author": "Dr. Lisa Park"},
    "content": """CLINICAL LABORATORY — TURNAROUND TIME IMPROVEMENT REPORT
Date: 2026-03-10 | Author: Dr. Lisa Park, Laboratory Director

EXECUTIVE SUMMARY:
The Clinical Laboratory has achieved significant improvements in test turnaround times (TAT) during Q1 2026 through process automation and workflow redesign. These improvements directly support clinical decision-making and patient throughput.

KEY METRICS:
- Complete Blood Count (CBC): TAT reduced from 58 min to 22 min (62% improvement)
- Basic Metabolic Panel (BMP): TAT reduced from 72 min to 31 min (57% improvement)
- Troponin (STAT): TAT reduced from 45 min to 18 min (60% improvement)
- Blood culture preliminary results: Reduced from 48 hours to 24 hours
- Critical value notification: Average 6 minutes from result to clinician notification

AUTOMATION INVESTMENTS:
The new Beckman Coulter DxA 5000 laboratory automation system was installed in January 2026. This system automates sample receiving, centrifugation, aliquoting, and routing to analytical instruments. It has reduced manual handling steps by 80% and virtually eliminated sample labeling errors.

IMPACT ON PATIENT CARE:
Faster lab results have enabled the Emergency Department to reduce average decision-to-disposition times by 35 minutes. The hospital's sepsis bundle compliance (including lactate result within 1 hour) improved from 72% to 94%.

QUALITY INDICATORS:
- Specimen rejection rate: 0.8% (down from 2.1%)
- Critical value notification compliance: 99.6%
- Proficiency testing scores: 100% satisfactory across all disciplines

Prepared by: Dr. Lisa Park, MD, PhD
Director, Clinical Laboratory Services"""
}

DOC_12 = {
    "filename": "12_Pharmacy_Inventory_Report.pdf",
    "type": "pdf",
    "metadata": {"department": "Pharmacy", "date": "2026-03-20", "source_type": "report", "author": "James Wright"},
    "content": """PHARMACY DEPARTMENT — Q1 2026 INVENTORY AND SAFETY REPORT
Date: 2026-03-20 | Author: James Wright, PharmD, Director of Pharmacy

MEDICATION SAFETY HIGHLIGHTS:
Zero medication-related sentinel events during Q1 2026. This continues our streak of 18 consecutive months without a sentinel event, the longest in the hospital's history. The automated dispensing system (Pyxis MedStation ES) flagged and prevented 847 potential medication errors during the quarter, including 23 high-severity interactions.

CONTROLLED SUBSTANCE COMPLIANCE:
All quarterly DEA audits passed with zero discrepancies. Controlled substance waste documentation compliance: 99.8%. Automated narcotic inventory discrepancy investigations: 3 (all resolved within 24 hours, attributed to documentation timing errors).

FORMULARY MANAGEMENT:
The Pharmacy and Therapeutics Committee approved the addition of 4 new medications to the formulary and removed 6 medications with superior alternatives available. Biosimilar utilization increased from 45% to 68%, generating estimated savings of $340,000.

CRITICAL DRUG SHORTAGE MANAGEMENT:
Successfully managed 12 drug shortage situations during Q1 without any patient care disruptions. Alternative sourcing strategies and therapeutic substitutions were implemented proactively for all affected medications.

Prepared by: James Wright, PharmD, BCPS
Director of Pharmacy Services"""
}

DOC_13 = {
    "filename": "13_Pediatric_Ward_Report.pdf",
    "type": "pdf",
    "metadata": {"department": "Pediatrics", "date": "2026-03-25", "source_type": "report", "author": "Dr. Emily Watson"},
    "content": """PEDIATRIC DEPARTMENT — Q1 2026 PERFORMANCE REPORT
Date: 2026-03-25 | Author: Dr. Emily Watson, Chief of Pediatrics

PATIENT SATISFACTION:
The Pediatric Ward achieved a satisfaction score of 4.7 out of 5.0, the highest of any department in Q1 2026. This is consistent with the hospital-wide patient satisfaction improvement reported by the Patient Relations Department. Key drivers of satisfaction include:

- Play therapy program (introduced February 2026): 96% of families rated it "Excellent"
- Child Life specialist coverage expanded to evenings and weekends
- New family sleeping accommodations in all pediatric rooms
- Pediatric-specific meal menu developed with input from patients and families

CLINICAL OUTCOMES:
- Average length of stay: 3.2 days (below national pediatric benchmark of 3.8 days)
- Readmission rate (30-day): 2.1% (national benchmark: 6.5%)
- Hospital-acquired conditions: Zero cases during Q1
- Central line infections (PICU): Zero cases during Q1

COMMUNITY OUTREACH:
The department hosted 8 community education sessions on childhood asthma management, serving 340 families. Three school-based health screenings were conducted, identifying 12 children requiring follow-up care.

Prepared by: Dr. Emily Watson, MD, FAAP
Chief of Pediatrics"""
}

DOC_14 = {
    "filename": "14_Security_Incident_Log.txt",
    "type": "txt",
    "metadata": {"department": "Security", "date": "2026-03-31", "source_type": "log", "author": "Chief Derek Morgan"},
    "content": """HOSPITAL SECURITY — Q1 2026 INCIDENT SUMMARY
Compiled by: Chief Derek Morgan, Director of Hospital Security
Date: 2026-03-31

TOTAL INCIDENTS: 89 (Q4 2025: 102, representing a 13% reduction)

INCIDENT CATEGORIES:
1. Workplace Violence: 12 incidents (8 patient-on-staff, 4 visitor-related)
2. Elopement Attempts: 7 (all patients returned safely, 3 behavioral health)
3. Theft: 15 (9 personal property, 4 equipment, 2 medication diversion — referred to pharmacy)
4. Trespassing: 8 (unauthorized visitors after hours, no security breaches to restricted areas)
5. Behavioral Disturbances: 23 (primarily in Emergency Department during peak wait times)
6. Motor Vehicle Incidents: 6 (parking structure, no injuries)
7. Fire Alarm Activations: 4 (all false alarms, 2 attributed to construction dust)
8. Other: 14 (lost and found, escort requests, welfare checks)

NOTABLE IMPROVEMENT:
The new visitor management system (implemented January 2026) has reduced unauthorized access incidents by 62%. All visitors now receive photo ID badges that expire at the end of their visit. The system has also aided law enforcement in one active investigation.

NEW BODY-WORN CAMERA PROGRAM:
Body-worn cameras were deployed to all security officers on February 1. In the first two months, footage was requested for 6 incident investigations and proved instrumental in resolving 4 of them, including 2 workplace violence complaints.

Prepared by: Chief Derek Morgan
Director of Hospital Security"""
}

DOC_15 = {
    "filename": "15_Training_Completion_Report.pdf",
    "type": "pdf",
    "metadata": {"department": "Education", "date": "2026-03-28", "source_type": "report", "author": "Linda Torres"},
    "content": """STAFF EDUCATION — Q1 2026 TRAINING COMPLIANCE REPORT
Date: 2026-03-28 | Author: Linda Torres, Director of Staff Education

MANDATORY TRAINING COMPLIANCE:
Overall compliance rate for Q1 mandatory training: 97.2% (target: 95%)

TRAINING MODULE COMPLETION RATES:
1. HIPAA Privacy & Security: 99.1%
2. Fire Safety & Emergency Codes: 98.4%
3. Infection Prevention (Annual): 96.8%
4. Workplace Violence Prevention: 95.3%
5. Cultural Competency: 94.7%
6. Fall Prevention Protocol: 97.9%
7. Blood-borne Pathogen Exposure: 98.2%
8. Restraint & Seclusion Policy: 96.1%

SPECIALTY TRAINING HIGHLIGHTS:
- 95% of patient-facing staff completed the new Hospitality Excellence training program (this program is credited with the hospital-wide improvement in patient satisfaction scores)
- 23 nurses completed Advanced Cardiac Life Support (ACLS) recertification
- 8 MRI technologists completed Siemens MAGNETOM certification
- 15 ED nurses completed Trauma Nursing Core Course (TNCC)
- 12 pharmacists completed sterile compounding recertification

SIMULATION CENTER:
The new simulation center conducted 34 team-based simulation exercises, training 412 staff members in high-risk scenarios including cardiac arrest, obstetric emergency, and mass casualty triage. Post-simulation confidence scores improved by an average of 28%.

Prepared by: Linda Torres, MEd
Director of Staff Education"""
}

DOC_16 = {
    "filename": "16_Dietary_Services_Report.pdf",
    "type": "pdf",
    "metadata": {"department": "Dietary", "date": "2026-03-15", "source_type": "report", "author": "Chef Antonio Rossi"},
    "content": """DIETARY SERVICES — Q1 2026 PERFORMANCE REPORT
Date: 2026-03-15 | Author: Chef Antonio Rossi, Director of Dietary Services

PATIENT MEAL SATISFACTION:
Patient meal satisfaction scores improved from 3.1/5.0 in Q4 2025 to 3.9/5.0 in Q1 2026 following the implementation of our "Fresh First" initiative. This initiative replaced 40% of previously frozen meal components with fresh, locally sourced ingredients.

MENU IMPROVEMENTS:
- New rotating 4-week menu cycle with 12 entree options per meal period
- Introduction of culturally diverse meal options (Halal, Kosher, South Asian, Latin American)
- New allergen-free meal preparation area, eliminating cross-contamination risks
- Bedside meal ordering system allowing patients to order within a 2-hour window before each meal

THERAPEUTIC DIET COMPLIANCE:
Accuracy of therapeutic diet delivery improved to 98.5% (up from 93.2%). Real-time diet order integration with the electronic health record (EHR) has virtually eliminated transcription errors. Registered Dietitian assessments within 24 hours of admission: 94% compliance.

FOOD SAFETY:
Zero food-borne illness incidents. Health department inspection score: 98/100 (highest in the county). All food handlers completed ServSafe certification renewal during the quarter.

COST MANAGEMENT:
Despite the shift to higher-quality ingredients, food cost per patient day increased by only 4% ($12.80 to $13.31) due to waste reduction initiatives and local sourcing partnerships.

Prepared by: Chef Antonio Rossi
Director of Dietary Services"""
}

DOC_17 = {
    "filename": "17_IT_Systems_Uptime_Report.txt",
    "type": "txt",
    "metadata": {"department": "Information Technology", "date": "2026-03-31", "source_type": "report", "author": "Priya Sharma"},
    "content": """IT DEPARTMENT — Q1 2026 SYSTEMS UPTIME AND PERFORMANCE REPORT
Author: Priya Sharma, CIO / VP of Information Technology
Date: 2026-03-31

SYSTEM AVAILABILITY:
Overall IT systems uptime: 99.97% (target: 99.9%)
- Electronic Health Record (Epic): 99.99% uptime, zero unplanned downtime
- Laboratory Information System: 99.98% uptime
- Pharmacy Dispensing System (Pyxis): 99.95% uptime
- PACS (Medical Imaging): 99.96% uptime
- Nurse Call System: 100% uptime
- Building Management System: 99.94% uptime

PLANNED MAINTENANCE WINDOWS:
Three planned maintenance windows were executed during Q1 (all between 2:00-5:00 AM Sunday mornings):
- January 12: Epic upgrade to February 2026 release (new sepsis screening alert)
- February 9: Network infrastructure firmware updates (security patches)
- March 9: PACS storage expansion (added 50TB for new MRI volume)

CYBERSECURITY:
- Phishing simulation tests conducted: 3 campaigns, 4,200 emails sent
- Click rate: 4.2% (down from 8.7% in Q4 2025, industry average: 12%)
- Zero successful ransomware or malware incidents
- Multi-factor authentication deployment: 100% of clinical systems
- Penetration test conducted by external firm (CrowdStrike): No critical vulnerabilities found

HELP DESK PERFORMANCE:
- Total tickets: 3,847
- Average response time: 12 minutes (target: 15 minutes)
- First-call resolution rate: 76%
- User satisfaction score: 4.2/5.0

Prepared by: Priya Sharma, MBA
Chief Information Officer"""
}

DOC_18 = {
    "filename": "18_Quality_Committee_Minutes.pdf",
    "type": "pdf",
    "metadata": {"department": "Quality", "date": "2026-03-28", "source_type": "minutes", "author": "Dr. Robert Kim"},
    "content": """QUALITY & PATIENT SAFETY COMMITTEE — MEETING MINUTES
Date: March 28, 2026 | Chair: Dr. Robert Kim, Chief Quality Officer
Attendees: 14 of 16 committee members present

AGENDA ITEM 1: PATIENT FALL REDUCTION
Q1 falls: 47 (Q4 2025: 62), a 24% reduction. Falls with injury: 8 (Q4: 14). The new bed alarm protocol and hourly rounding initiative appear to be effective. However, the committee noted that the majority of falls (31 of 47) occurred during night shifts, correlating with reports of reduced staffing. ACTION ITEM: Request nightshift staffing data from HR for correlation analysis.

AGENDA ITEM 2: HOSPITAL-ACQUIRED INFECTION DISCREPANCY
The committee reviewed conflicting reports regarding hospital-acquired infections. The Surgical Department reports a historic low of 1.2% SSI rate, while the ICU reports a concerning 4.5% HAI rate. Dr. Bailey and Nurse Kelly presented their respective data. The committee concluded that both reports are accurate for their respective departments, but that the hospital needs a unified infection reporting dashboard. ACTION ITEM: Task IT with developing a real-time infection tracking dashboard by end of Q2.

AGENDA ITEM 3: PATIENT EXPERIENCE DISCREPANCY
Members discussed the apparent contradiction between the Patient Relations Q1 Survey (showing 20% satisfaction improvement) and the Emergency Department Incident Log (showing 25% increase in complaints). After reviewing both documents, the committee noted that the Patient Relations survey primarily captures inpatient satisfaction (discharged patients), while the Emergency Department data reflects outpatient/walk-in experience. Both may be accurate simultaneously, but the hospital should not present only the positive data to the Board. ACTION ITEM: Request combined patient experience report for Board presentation.

AGENDA ITEM 4: READMISSION RATES
30-day readmission rate improved to 11.8% (Q4: 13.2%, national average: 15.2%). Heart failure readmissions showed the most improvement (18.3% to 12.7%) following implementation of the transition-of-care nursing program.

AGENDA ITEM 5: CORE MEASURES
CMS Core Measure compliance: 96.4% overall. AMI measures: 98.1%. Heart failure: 95.7%. Pneumonia: 97.2%. Surgical care: 94.6%. All measures exceed CMS benchmarks.

Next Meeting: April 25, 2026

Signed: Dr. Robert Kim, MD, MPH
Chief Quality Officer"""
}

# ─── All documents ────────────────────────────────────────────────────────────

ALL_DOCUMENTS = [
    DOC_01, DOC_02, DOC_03, DOC_04, DOC_05, DOC_06, DOC_07, DOC_08,
    DOC_09, DOC_10, DOC_11, DOC_12, DOC_13, DOC_14, DOC_15, DOC_16,
    DOC_17, DOC_18
]

def generate():
    # Clean old data
    for f in os.listdir(DATA_DIR):
        os.remove(os.path.join(DATA_DIR, f))

    for doc in ALL_DOCUMENTS:
        file_path = os.path.join(DATA_DIR, doc["filename"])

        if doc["type"] == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)

            # Title header
            dept = doc["metadata"].get("department", "Unknown")
            pdf.cell(0, 10, txt=f"CONFIDENTIAL - {dept} Department", ln=1, align="C")
            pdf.cell(0, 8, txt=f"Date: {doc['metadata']['date']} | Author: {doc['metadata']['author']}", ln=1, align="L")
            pdf.cell(0, 6, txt="-" * 80, ln=1, align="L")
            pdf.ln(4)

            # Body text
            for line in doc["content"].split("\n"):
                line = line.strip()
                if not line:
                    pdf.ln(3)
                else:
                    # Handle encoding — replace special chars for FPDF latin-1
                    safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
                    pdf.multi_cell(0, 5, txt=safe_line)

            pdf.output(file_path)

        else:  # txt or md
            with open(file_path, "w", encoding="utf-8") as f:
                meta_line = json.dumps(doc["metadata"])
                f.write(f"Metadata: {meta_line}\n\n")
                f.write(doc["content"].strip())

    print(f"\n{'='*60}")
    print(f"Generated {len(ALL_DOCUMENTS)} rich documents in {DATA_DIR}")
    print(f"{'='*60}")
    print("\nConflict Pairs:")
    print("  1. Patient Satisfaction: Doc 01 (+20%) vs Doc 02 (ER complaints +25%)")
    print("  2. MRI Machine: Doc 03 (operational) vs Doc 04 (delayed/broken)")
    print("  3. Infection Rates: Doc 05 (1.2% SSI) vs Doc 06 (4.5% ICU HAI)")
    print("  4. Staffing: Doc 07 (100% staffed) vs Doc 08 (severe shortages)")
    print("  5. Costs: Doc 09 (overtime down) vs Doc 10 (overtime doubled)")
    print("\nNon-Conflict Documents:")
    print("  Doc 11: Lab Turnaround      Doc 12: Pharmacy Safety")
    print("  Doc 13: Pediatric Ward       Doc 14: Security Incidents")
    print("  Doc 15: Training Compliance  Doc 16: Dietary Services")
    print("  Doc 17: IT Systems Uptime    Doc 18: Quality Committee Minutes")

if __name__ == "__main__":
    generate()
