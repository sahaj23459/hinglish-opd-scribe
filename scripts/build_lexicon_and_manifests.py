"""Generate curated SNOMED CT Hinglish & Kannada lexicons plus synthetic OPD consult manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
LEXICON_DIR = ROOT / "data" / "lexicon"
MANIFEST_DIR = ROOT / "data" / "manifests"


def build_hinglish_lexicon() -> Dict[str, object]:
    """Return 105 verified SNOMED CT concepts covering Fever/AMR, Cardiometabolic, GI/Pain, and Drugs."""
    concepts: List[Dict[str, object]] = [
        # --- DOMAIN 1: Acute Febrile Illness, URI & AMR ---
        {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "pyrexia", "synonyms": ["bukhar", "tez bukhar", "badan garam", "halka bukhar", "fever"]},
        {"snomed_code": "43724002", "preferred_term": "Chill", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "pyrexia", "synonyms": ["kapkapi", "thand lagna", "thand lag kar bukhar", "chills", "shivering"]},
        {"snomed_code": "84229001", "preferred_term": "Fatigue", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "malaise", "synonyms": ["kamzori", "thakan", "fatigue", "weakness"], "ambiguous_triggers": ["badan tootna", "badan toot raha"]},
        {"snomed_code": "13791008", "preferred_term": "Asthenia", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "malaise", "synonyms": ["bahut kamzori", "uthne ki himmat nahi", "debility"]},
        {"snomed_code": "271807003", "preferred_term": "Eruption of skin", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "derm", "sub_branch": "exanthem", "synonyms": ["daane", "lal daane", "rash", "skin rash", "sharir par daane"]},
        {"snomed_code": "52613005", "preferred_term": "Excessive sweating", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "autonomic", "synonyms": ["paseena aana", "raat ko paseena", "thandha paseena"]},
        {"snomed_code": "89362005", "preferred_term": "Weight loss", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "nutrition", "synonyms": ["wazan kam hona", "weight loss", "wazan ghat gaya"]},
        {"snomed_code": "161838008", "preferred_term": "Loss of appetite", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "gi", "sub_branch": "appetite", "synonyms": ["bhookh nahi lagti", "bhookh kam hona", "khane ka man nahi", "loss of appetite"]},
        {"snomed_code": "38362002", "preferred_term": "Dengue", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "vector_borne", "synonyms": ["dengue", "dengue bukhar"]},
        {"snomed_code": "61462000", "preferred_term": "Malaria", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "vector_borne", "synonyms": ["malaria", "malaria bukhar"]},
        {"snomed_code": "4834000", "preferred_term": "Typhoid fever", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "enteric_infection", "synonyms": ["typhoid", "motijhara"]},
        {"snomed_code": "195662009", "preferred_term": "Acute viral pharyngitis", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["viral throat infection", "viral pharyngitis", "gale ka viral"]},
        {"snomed_code": "49727002", "preferred_term": "Cough", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "cough", "synonyms": ["khansi", "cough"]},
        {"snomed_code": "11833005", "preferred_term": "Dry cough", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "cough", "synonyms": ["sukhi khansi", "dry cough"]},
        {"snomed_code": "28743005", "preferred_term": "Productive cough", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "cough", "synonyms": ["balgam wali khansi", "wet cough", "balgam aana"]},
        {"snomed_code": "82272006", "preferred_term": "Common cold", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["zukam", "sardi zukam", "common cold"]},
        {"snomed_code": "64531003", "preferred_term": "Nasal discharge", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["naak behna", "runny nose", "naak se pani"]},
        {"snomed_code": "68235000", "preferred_term": "Nasal congestion", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["naak band", "blocked nose", "band naak"]},
        {"snomed_code": "162397003", "preferred_term": "Pain in throat", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["gale mein dard", "gale mein kharash", "throat pain", "sore throat", "gala kharab"]},
        {"snomed_code": "50219008", "preferred_term": "Hoarse voice", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["awaaz baith gayi", "hoarse voice"]},
        {"snomed_code": "267036007", "preferred_term": "Dyspnea", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "lower_respiratory", "synonyms": ["saans phoolna", "saans phoolti", "saans lene mein takleef", "breathlessness", "shortness of breath"]},
        {"snomed_code": "56018004", "preferred_term": "Wheezing", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "lower_respiratory", "synonyms": ["wheezing", "saans mein seeti"]},
        {"snomed_code": "195967001", "preferred_term": "Asthma", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "lower_respiratory", "synonyms": ["dama", "asthma"]},
        {"snomed_code": "233604007", "preferred_term": "Pneumonia", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "lower_respiratory", "synonyms": ["pneumonia", "phephde mein infection"]},
        {"snomed_code": "16001004", "preferred_term": "Otalgia", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "ent", "synonyms": ["kaan mein dard", "ear pain"]},
        {"snomed_code": "398979000", "preferred_term": "Red eye", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "neuro", "sub_branch": "ophthalmic", "synonyms": ["aankh lal hona", "red eye"]},
        {"snomed_code": "36955009", "preferred_term": "Loss of taste", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "neuro", "sub_branch": "sensory", "synonyms": ["swaad nahi aata", "loss of taste"]},
        {"snomed_code": "44169009", "preferred_term": "Loss of sense of smell", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "neuro", "sub_branch": "sensory", "synonyms": ["khushboo nahi aati", "loss of smell"]},

        # --- DOMAIN 2: Cardiometabolic Chronic Care (T2DM, HTN, Neuro/Vascular) ---
        {"snomed_code": "44054006", "preferred_term": "Diabetes mellitus type 2", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["diabetes", "type 2 diabetes", "sugar ki bimari", "madhumeh"]},
        {"snomed_code": "80394007", "preferred_term": "Hyperglycemia", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["sugar high", "sugar badh gayi", "high blood sugar", "fasting sugar high"], "ambiguous_triggers": ["sugar badha"]},
        {"snomed_code": "302866003", "preferred_term": "Hypoglycemia", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["sugar low", "sugar gir gayi", "low blood sugar"]},
        {"snomed_code": "38341003", "preferred_term": "Hypertensive disorder", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "blood_pressure", "synonyms": ["hypertension", "bp high", "high bp", "bp ki bimari", "uchch raktchaap"]},
        {"snomed_code": "45007003", "preferred_term": "Low blood pressure", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "blood_pressure", "synonyms": ["bp low", "low bp", "hypotension"]},
        {"snomed_code": "29857009", "preferred_term": "Chest pain", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "ischemic", "synonyms": ["seene mein dard", "chhati mein dard", "chest pain"]},
        {"snomed_code": "80313002", "preferred_term": "Palpitations", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "arrhythmia", "synonyms": ["dhadkan tez", "dil ki dhadkan badhna", "palpitations"], "ambiguous_triggers": ["ghabrahat"]},
        {"snomed_code": "56265001", "preferred_term": "Heart disease", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "ischemic", "synonyms": ["heart problem", "dil ki bimari", "heart disease", "cardiac problem"]},
        {"snomed_code": "13644009", "preferred_term": "Hypercholesterolemia", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "lipid", "synonyms": ["high cholesterol", "cholesterol badha hua"]},
        {"snomed_code": "247355005", "preferred_term": "Edema of foot", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "fluid_overload", "synonyms": ["paer mein sujan", "paeron mein sujan", "pedal edema", "ankle swelling"]},
        {"snomed_code": "28442001", "preferred_term": "Polyuria", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["baar baar peshab", "zyada peshab aana", "polyuria"]},
        {"snomed_code": "62106007", "preferred_term": "Nocturia", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["raat ko baar baar peshab", "nocturia"]},
        {"snomed_code": "161832001", "preferred_term": "Polydipsia", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["zyada pyaas lagna", "gala sookhna", "polydipsia"]},
        {"snomed_code": "302226006", "preferred_term": "Peripheral neuropathy", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "neuropathy", "synonyms": ["paer mein jhanjhanahat", "paeron mein jhanjhanahat", "tingling in feet", "peripheral neuropathy"]},
        {"snomed_code": "44077006", "preferred_term": "Numbness", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "neuropathy", "synonyms": ["sunnapan", "paer sunn hona", "numbness"]},
        {"snomed_code": "246636008", "preferred_term": "Blurred vision", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "ophthalmic", "synonyms": ["dhundhla dikhna", "blurred vision", "nazar dhundhli"]},
        {"snomed_code": "404640003", "preferred_term": "Dizziness", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "vestibular", "synonyms": ["dizziness", "sar ghoomna"], "ambiguous_triggers": ["chakkar aana", "chakkar"]},
        {"snomed_code": "399153001", "preferred_term": "Vertigo", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "vestibular", "synonyms": ["kamra ghoomna", "spinning vertigo"]},
        {"snomed_code": "271594007", "preferred_term": "Syncope", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "vestibular", "synonyms": ["behosh hona", "fainting", "chakkar kha kar girna"]},
        {"snomed_code": "236425005", "preferred_term": "Chronic kidney disease", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "systemic", "sub_branch": "renal", "synonyms": ["kidney ki bimari", "ckd", "gurde kamzor"]},
        {"snomed_code": "271737000", "preferred_term": "Anemia", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "systemic", "sub_branch": "hematologic", "synonyms": ["khoon ki kami", "anemia", "low hemoglobin"]},

        # --- DOMAIN 3: GI, Musculoskeletal, Neuro Pain & General OPD ---
        {"snomed_code": "25064002", "preferred_term": "Headache", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "neuro", "sub_branch": "headache", "synonyms": ["sir mein dard", "sir dard", "headache"]},
        {"snomed_code": "37796009", "preferred_term": "Migraine", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "neuro", "sub_branch": "headache", "synonyms": ["migraine", "aadhe sir ka dard"]},
        {"snomed_code": "193462001", "preferred_term": "Insomnia", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "neuro", "sub_branch": "sleep", "synonyms": ["neend nahi aati", "insomnia", "raat ko neend kharab"]},
        {"snomed_code": "162076009", "preferred_term": "Abdominal bloating", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["pet phoolna", "abdominal bloating", "pet bhari lagna"], "ambiguous_triggers": ["gas banti hai", "pet mein gas", "gas"]},
        {"snomed_code": "249497008", "preferred_term": "Flatulence", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["flatulence", "gas paas hona"]},
        {"snomed_code": "16331000", "preferred_term": "Heartburn", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["seene mein jalan", "acidity", "pet mein jalan", "heartburn"]},
        {"snomed_code": "249496004", "preferred_term": "Eructation", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["khatti dakar", "dakar aana", "sour belching"]},
        {"snomed_code": "162031009", "preferred_term": "Indigestion", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["badhazmi", "khana hazam nahi hota", "indigestion"]},
        {"snomed_code": "21522001", "preferred_term": "Abdominal pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "gi_pain", "synonyms": ["pet mein dard", "pet dard", "pet mein marod", "abdominal pain"]},
        {"snomed_code": "79922009", "preferred_term": "Epigastric pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "gi_pain", "synonyms": ["upar pet mein dard", "epigastric pain"]},
        {"snomed_code": "422587007", "preferred_term": "Nausea", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "emesis", "synonyms": ["ji machlana", "matli", "nausea", "ulti jaisa lagna"]},
        {"snomed_code": "422400008", "preferred_term": "Vomiting", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "emesis", "synonyms": ["ulti", "ulti hona", "vomiting"]},
        {"snomed_code": "62315008", "preferred_term": "Diarrhea", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "bowel", "synonyms": ["dast", "loose motion", "patle dast", "diarrhea"]},
        {"snomed_code": "14760008", "preferred_term": "Constipation", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "bowel", "synonyms": ["qabz", "pet saaf nahi hota", "constipation"]},
        {"snomed_code": "4556007", "preferred_term": "Gastritis", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["gastritis", "pet mein sujan"]},
        {"snomed_code": "235595009", "preferred_term": "Gastroesophageal reflux disease", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["gerd", "acid reflux"]},
        {"snomed_code": "40739000", "preferred_term": "Dysphagia", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "esophageal", "synonyms": ["nigalne mein takleef", "difficulty swallowing"]},
        {"snomed_code": "18165001", "preferred_term": "Jaundice", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "hepatic", "synonyms": ["peeliya", "jaundice"]},
        {"snomed_code": "26284000", "preferred_term": "Ulcer of mouth", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "oral", "synonyms": ["muh mein chhale", "mouth ulcer"]},
        {"snomed_code": "68962001", "preferred_term": "Muscle pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "myalgia", "synonyms": ["badan dard", "maanspeshiyon mein dard", "body ache", "myalgia"]},
        {"snomed_code": "71315009", "preferred_term": "Muscle cramp in leg", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "myalgia", "synonyms": ["pindli mein nas chadhna", "leg cramps"]},
        {"snomed_code": "57676002", "preferred_term": "Joint pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "arthralgia", "synonyms": ["jodon mein dard", "joint pain", "arthralgia"]},
        {"snomed_code": "30989003", "preferred_term": "Knee pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "arthralgia", "synonyms": ["ghutne mein dard", "knee pain"]},
        {"snomed_code": "45326000", "preferred_term": "Shoulder pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "arthralgia", "synonyms": ["kandhe mein dard", "shoulder pain"]},
        {"snomed_code": "161891005", "preferred_term": "Backache", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "spine", "synonyms": ["kamar mein dard", "peeth mein dard", "backache", "back pain"]},
        {"snomed_code": "81680005", "preferred_term": "Neck pain", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "spine", "synonyms": ["gardan mein dard", "neck pain"]},
        {"snomed_code": "396275006", "preferred_term": "Osteoarthritis", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "musculoskeletal", "sub_branch": "arthralgia", "synonyms": ["osteoarthritis", "gathiya"]},
        {"snomed_code": "49650001", "preferred_term": "Dysuria", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "systemic", "sub_branch": "urinary", "synonyms": ["peshab mein jalan", "burning urination"]},
        {"snomed_code": "68566005", "preferred_term": "Urinary tract infection", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "systemic", "sub_branch": "urinary", "synonyms": ["urine infection", "uti"]},
        {"snomed_code": "418290006", "preferred_term": "Itching", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "derm", "sub_branch": "pruritus", "synonyms": ["khujli", "itching"]},
        {"snomed_code": "126485001", "preferred_term": "Urticaria", "semantic_tag": "disorder", "clinical_domain": "gi_musculoskeletal", "organ_branch": "derm", "sub_branch": "pruritus", "synonyms": ["pitti uchhalna", "hives", "urticaria"]},

        # --- MEDICATIONS & ANTIMICROBIALS (SNOMED CT Substance/Product Codes) ---
        {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "analgesic_antipyretic", "synonyms": ["paracetamol", "dolo", "crocin", "calpol", "pcm"]},
        {"snomed_code": "387207008", "preferred_term": "Ibuprofen", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "nsaid", "synonyms": ["ibuprofen", "brufen", "combiflam"]},
        {"snomed_code": "703125008", "preferred_term": "Diclofenac", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "nsaid", "synonyms": ["diclofenac", "voveran"]},
        {"snomed_code": "387531004", "preferred_term": "Azithromycin", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antibiotic", "synonyms": ["azithromycin", "azee", "azithral"]},
        {"snomed_code": "372687004", "preferred_term": "Amoxicillin", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antibiotic", "synonyms": ["amoxicillin", "augmentin", "mox"]},
        {"snomed_code": "372840008", "preferred_term": "Ciprofloxacin", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antibiotic", "synonyms": ["ciprofloxacin", "cifran"]},
        {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antibiotic", "synonyms": ["antibiotic", "antibiotics"]},
        {"snomed_code": "372887000", "preferred_term": "Cetirizine", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antihistamine", "synonyms": ["cetirizine", "okacet", "levocetirizine"]},
        {"snomed_code": "372729009", "preferred_term": "Montelukast", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "respiratory_drug", "synonyms": ["montelukast", "montair"]},
        {"snomed_code": "387475002", "preferred_term": "Salbutamol", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "respiratory_drug", "synonyms": ["salbutamol", "asthalin"]},
        {"snomed_code": "372567009", "preferred_term": "Metformin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antidiabetic", "synonyms": ["metformin", "glycomet"]},
        {"snomed_code": "373492002", "preferred_term": "Glimepiride", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antidiabetic", "synonyms": ["glimepiride", "amaryl"]},
        {"snomed_code": "412261000", "preferred_term": "Sitagliptin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antidiabetic", "synonyms": ["sitagliptin", "januvia"]},
        {"snomed_code": "67866001", "preferred_term": "Insulin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antidiabetic", "synonyms": ["insulin"]},
        {"snomed_code": "386864001", "preferred_term": "Amlodipine", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antihypertensive", "synonyms": ["amlodipine", "stamlo"]},
        {"snomed_code": "373529000", "preferred_term": "Telmisartan", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antihypertensive", "synonyms": ["telmisartan", "telma"]},
        {"snomed_code": "387094007", "preferred_term": "Losartan", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antihypertensive", "synonyms": ["losartan"]},
        {"snomed_code": "372733002", "preferred_term": "Metoprolol", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antihypertensive", "synonyms": ["metoprolol"]},
        {"snomed_code": "372912004", "preferred_term": "Atorvastatin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "statin", "synonyms": ["atorvastatin", "lipitor"]},
        {"snomed_code": "387458008", "preferred_term": "Aspirin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antiplatelet", "synonyms": ["aspirin", "ecosprin"]},
        {"snomed_code": "395821003", "preferred_term": "Pantoprazole", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "ppi", "synonyms": ["pantoprazole", "pan 40", "pan d"]},
        {"snomed_code": "387137007", "preferred_term": "Omeprazole", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "ppi", "synonyms": ["omeprazole", "omez"]},
        {"snomed_code": "387311004", "preferred_term": "Domperidone", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "antiemetic", "synonyms": ["domperidone"]},
        {"snomed_code": "372487007", "preferred_term": "Ondansetron", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "antiemetic", "synonyms": ["ondansetron", "emeset"]},
        {"snomed_code": "387077008", "preferred_term": "Oral rehydration salts", "semantic_tag": "medication", "clinical_domain": "gi_musculoskeletal", "organ_branch": "drug", "sub_branch": "electrolyte", "synonyms": ["ors", "electral"]},
        {"snomed_code": "387086006", "preferred_term": "Cyanocobalamin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "vitamin", "synonyms": ["vitamin b12", "methylcobalamin", "neurobion"]},
    ]
    return {
        "lexicon_name": "Hinglish-SNOMED-OPD-Core-v1",
        "language": "hi-Latn / hi-Deva / en-IN",
        "snomed_edition": "SNOMED CT International + NRCES India Subset",
        "num_concepts": len(concepts),
        "concepts": concepts,
    }


def build_kannada_lexicon() -> Dict[str, object]:
    """Return swappable Kannada SNOMED CT lexicon proving zero-code-change Karnataka portability."""
    concepts: List[Dict[str, object]] = [
        {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "systemic", "sub_branch": "pyrexia", "synonyms": ["jvara", "ಜ್ವರ", "fever"]},
        {"snomed_code": "49727002", "preferred_term": "Cough", "semantic_tag": "finding", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "cough", "synonyms": ["kemmu", "ಕೆಮ್ಮು", "cough"]},
        {"snomed_code": "82272006", "preferred_term": "Common cold", "semantic_tag": "disorder", "clinical_domain": "acute_febrile_amr", "organ_branch": "respiratory", "sub_branch": "upper_respiratory", "synonyms": ["sheeta", "ಶೀತ", "cold"]},
        {"snomed_code": "25064002", "preferred_term": "Headache", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "neuro", "sub_branch": "headache", "synonyms": ["talenovu", "ತಲೆನೋವು", "headache"]},
        {"snomed_code": "162076009", "preferred_term": "Abdominal bloating", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["hotte ubbara", "ಹೊಟ್ಟೆ ಉಬ್ಬರ"], "ambiguous_triggers": ["gas", "ಗ್ಯಾಸ್"]},
        {"snomed_code": "16331000", "preferred_term": "Heartburn", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "dyspepsia_gas", "synonyms": ["ede uri", "ಎದೆ ಉರಿ", "acidity"]},
        {"snomed_code": "404640003", "preferred_term": "Dizziness", "semantic_tag": "finding", "clinical_domain": "cardiometabolic", "organ_branch": "neuro", "sub_branch": "vestibular", "synonyms": ["talesuttu", "ತಲೆಸುತ್ತು"]},
        {"snomed_code": "422400008", "preferred_term": "Vomiting", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "emesis", "synonyms": ["vaanti", "ವಾಂತಿ"]},
        {"snomed_code": "62315008", "preferred_term": "Diarrhea", "semantic_tag": "finding", "clinical_domain": "gi_musculoskeletal", "organ_branch": "gi", "sub_branch": "bowel", "synonyms": ["bhedi", "ಭೇದಿ"]},
        {"snomed_code": "44054006", "preferred_term": "Diabetes mellitus type 2", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "endocrine", "sub_branch": "glycemic", "synonyms": ["sakkare kaayile", "ಸಕ್ಕರೆ ಕಾಯಿಲೆ", "diabetes"]},
        {"snomed_code": "38341003", "preferred_term": "Hypertensive disorder", "semantic_tag": "disorder", "clinical_domain": "cardiometabolic", "organ_branch": "cardiac", "sub_branch": "blood_pressure", "synonyms": ["bp", "ಬಿಪಿ", "high bp"]},
        {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "analgesic_antipyretic", "synonyms": ["paracetamol", "ಪ್ಯಾರಾಸಿಟಮಾಲ್"]},
        {"snomed_code": "372567009", "preferred_term": "Metformin", "semantic_tag": "medication", "clinical_domain": "cardiometabolic", "organ_branch": "drug", "sub_branch": "antidiabetic", "synonyms": ["metformin", "ಮೆಟ್ಫಾರ್ಮಿನ್"]},
        {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "clinical_domain": "acute_febrile_amr", "organ_branch": "drug", "sub_branch": "antibiotic", "synonyms": ["antibiotic", "ಆಂಟಿಬಯೋಟಿಕ್"]},
    ]
    return {
        "lexicon_name": "Kannada-SNOMED-Portability-Plugin-v1",
        "language": "kn-IN",
        "num_concepts": len(concepts),
        "concepts": concepts,
    }


def build_pilot_consults() -> List[Dict[str, object]]:
    """Build 24 scripted multi-turn Hinglish OPD consults (8 dev + 16 locked held-out test)."""
    consults: List[Dict[str, object]] = [
        # ==================== LOCKED HELD-OUT TEST SPLIT (16 CONSULTS) ====================
        {
            "consult_id": "OPD-T01",
            "split": "test",
            "domain": "acute_febrile_amr",
            "stress_tags": ["negation", "fractional_dose", "amr_stewardship"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "डॉक्टर साहब, मुझे तीन दिन से बुखार है, पर सिर में दर्द नहीं है।", "text_ref": "doctor sahab mujhe teen din se bukhar hai par sir mein dard nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Paracetamol डेढ़ गोली सुबह शाम लीजिए, viral में antibiotic मत लीजिए।", "text_ref": "paracetamol dedh goli subah shaam lijiye viral mein antibiotic mat lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "25064002", "preferred_term": "Headache", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.5},
                {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "OPD-T02",
            "split": "test",
            "domain": "acute_febrile_amr",
            "stress_tags": ["negation", "amr_stewardship"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "मुझे चार दिन से सूखी खांसी और गले में दर्द है, पर सांस फूलना नहीं है।", "text_ref": "mujhe chaar din se sukhi khansi aur gale mein dard hai par saans phoolna nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Cetirizine एक गोली रात को लें, Azithromycin मत लें।", "text_ref": "cetirizine ek goli raat ko lein azithromycin mat lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "11833005", "preferred_term": "Dry cough", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 4.0, "duration_unit": "d"},
                {"snomed_code": "162397003", "preferred_term": "Pain in throat", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "267036007", "preferred_term": "Dyspnea", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372887000", "preferred_term": "Cetirizine", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
                {"snomed_code": "387531004", "preferred_term": "Azithromycin", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "OPD-T03",
            "split": "test",
            "domain": "acute_febrile_amr",
            "stress_tags": ["negation", "vector_borne"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "दो दिन से तेज़ बुखार और कपकपी है, लेकिन शरीर पर लाल दाने नहीं हैं।", "text_ref": "do din se tez bukhar aur kapkapi hai lekin sharir par lal daane nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Paracetamol एक गोली लीजिए और कल खून की जांच कराएं।", "text_ref": "paracetamol ek goli lijiye aur kal khoon ki jaanch karayein"},
            ],
            "gold_annotations": [
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "d"},
                {"snomed_code": "43724002", "preferred_term": "Chill", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "271807003", "preferred_term": "Eruption of skin", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T04",
            "split": "test",
            "domain": "acute_febrile_amr",
            "stress_tags": ["idiom", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "पांच दिन से सर्दी जुकाम है और बदन टूट रहा है, पर उल्टी नहीं है।", "text_ref": "paanch din se sardi zukam hai aur badan toot raha hai par ulti nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "भाप लीजिए और Paracetamol आधी गोली जरूरत पड़ने पर लें।", "text_ref": "bhaap lijiye aur paracetamol aadhi goli zaroorat padne par lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "82272006", "preferred_term": "Common cold", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient", "duration_value": 5.0, "duration_unit": "d"},
                {"snomed_code": "84229001", "preferred_term": "Fatigue", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "422400008", "preferred_term": "Vomiting", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 0.5},
            ],
        },
        {
            "consult_id": "OPD-T05",
            "split": "test",
            "domain": "acute_febrile_amr",
            "stress_tags": ["attendant_turn", "negation"],
            "turns": [
                {"speaker": "attendant", "voice": "hi-IN-SwaraNeural", "text_tts": "डॉक्टर साहब, इनको तीन दिन से बलगम वाली खांसी है और भूख नहीं लगती।", "text_ref": "doctor sahab inko teen din se balgam wali khansi hai aur bhookh nahi lagti"},
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "हाँ पर सीने में दर्द नहीं है।", "text_ref": "haan par seene mein dard nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Amoxicillin एक गोली सुबह शाम पांच दिन तक लीजिए।", "text_ref": "amoxicillin ek goli subah shaam paanch din tak lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "28743005", "preferred_term": "Productive cough", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "161838008", "preferred_term": "Loss of appetite", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "29857009", "preferred_term": "Chest pain", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372687004", "preferred_term": "Amoxicillin", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T06",
            "split": "test",
            "domain": "cardiometabolic",
            "stress_tags": ["fractional_dose", "idiom", "ambiguous_chakkar"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "डॉक्टर साहब, दो महीने से शुगर बढ़ गई है और सुबह चक्कर आना होता है।", "text_ref": "doctor sahab do mahine se sugar badh gayi hai aur subah chakkar aana hota hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Metformin डेढ़ गोली सुबह शाम कर दीजिए।", "text_ref": "metformin dedh goli subah shaam kar dijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "80394007", "preferred_term": "Hyperglycemia", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "mo"},
                {"snomed_code": "404640003", "preferred_term": "Dizziness", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "372567009", "preferred_term": "Metformin", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.5},
            ],
        },
        {
            "consult_id": "OPD-T07",
            "split": "test",
            "domain": "cardiometabolic",
            "stress_tags": ["fractional_dose_dhai", "neuropathy", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "मुझे diabetes है, तीन महीने से पैर में झनझनाहट है पर पैर में सूजन नहीं है।", "text_ref": "mujhe diabetes hai teen mahine se paer mein jhanjhanahat hai par paer mein sujan nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Metformin ढाई गोली मत लीजिए, सिर्फ दो गोली लें और Vitamin B12 एक गोली रोज लें।", "text_ref": "metformin dhai goli mat lijiye sirf do goli lein aur vitamin b12 ek goli roz lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "44054006", "preferred_term": "Diabetes mellitus type 2", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "302226006", "preferred_term": "Peripheral neuropathy", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "mo"},
                {"snomed_code": "247355005", "preferred_term": "Edema of foot", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372567009", "preferred_term": "Metformin", "semantic_tag": "medication", "polarity": "negated", "subject": "patient", "dose_value": 2.5},
                {"snomed_code": "387086006", "preferred_term": "Cyanocobalamin", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T08",
            "split": "test",
            "domain": "cardiometabolic",
            "stress_tags": ["family_subject", "fractional_dose", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "मेरे पिताजी को दिल की बीमारी थी, मेरा BP high रहता है पर सीने में दर्द नहीं है।", "text_ref": "mere pitaji ko dil ki bimari thi mera bp high rehta hai par seene mein dard nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Amlodipine आधी गोली रोज सुबह लें और Telmisartan एक गोली जारी रखें।", "text_ref": "amlodipine aadhi goli roz subah lein aur telmisartan ek goli jaari rakhein"},
            ],
            "gold_annotations": [
                {"snomed_code": "56265001", "preferred_term": "Heart disease", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "family_member"},
                {"snomed_code": "38341003", "preferred_term": "Hypertensive disorder", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "29857009", "preferred_term": "Chest pain", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "386864001", "preferred_term": "Amlodipine", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 0.5},
                {"snomed_code": "373529000", "preferred_term": "Telmisartan", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T09",
            "split": "test",
            "domain": "cardiometabolic",
            "stress_tags": ["polyuria", "vision", "statin"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "एक महीने से बार बार पेशाब आता है और धुंधला दिखना शुरू हुआ है।", "text_ref": "ek mahine se baar baar peshab aata hai aur dhundhla dikhna shuru hua hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Glimepiride एक गोली नाश्ते से पहले और Atorvastatin एक गोली रात को लें।", "text_ref": "glimepiride ek goli naashte se pehle aur atorvastatin ek goli raat ko lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "28442001", "preferred_term": "Polyuria", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 1.0, "duration_unit": "mo"},
                {"snomed_code": "246636008", "preferred_term": "Blurred vision", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "373492002", "preferred_term": "Glimepiride", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
                {"snomed_code": "372912004", "preferred_term": "Atorvastatin", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T10",
            "split": "test",
            "domain": "cardiometabolic",
            "stress_tags": ["palpitations", "negation", "fractional_dose"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "सात दिन से दिल की धड़कन बढ़ना महसूस होता है, पर बेहोश होना नहीं हुआ।", "text_ref": "saat din se dil ki dhadkan badhna mehsoos hota hai par behosh hona nahi hua"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Metoprolol सवा गोली नहीं, सिर्फ आधी गोली सुबह लें।", "text_ref": "metoprolol sawa goli nahi sirf aadhi goli subah lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "80313002", "preferred_term": "Palpitations", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 7.0, "duration_unit": "d"},
                {"snomed_code": "271594007", "preferred_term": "Syncope", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372733002", "preferred_term": "Metoprolol", "semantic_tag": "medication", "polarity": "negated", "subject": "patient", "dose_value": 1.25},
            ],
        },
        {
            "consult_id": "OPD-T11",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["idiom_gas", "idiom_khatti_dakar", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "डॉक्टर साहब, दस दिन से पेट में गैस बनती है और खट्टी डकार आती है, पर उल्टी नहीं है।", "text_ref": "doctor sahab das din se pet mein gas banti hai aur khatti dakar aati hai par ulti nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Pantoprazole एक गोली सुबह खाली पेट लीजिए।", "text_ref": "pantoprazole ek goli subah khaali pet lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "162076009", "preferred_term": "Abdominal bloating", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 10.0, "duration_unit": "d"},
                {"snomed_code": "249496004", "preferred_term": "Eructation", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "422400008", "preferred_term": "Vomiting", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "395821003", "preferred_term": "Pantoprazole", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T12",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["laterality_left", "negation", "cardiac_ruleout"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "दो हफ्ते से बाएं कंधे में दर्द है, पर सीने में जलन नहीं है।", "text_ref": "do hafte se baayein kandhe mein dard hai par seene mein jalan nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Ibuprofen एक गोली खाने के बाद लें।", "text_ref": "ibuprofen ek goli khane ke baad lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "45326000", "preferred_term": "Shoulder pain", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "wk", "laterality": "left"},
                {"snomed_code": "16331000", "preferred_term": "Heartburn", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387207008", "preferred_term": "Ibuprofen", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T13",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["diarrhea", "ors", "amr_stewardship"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "कल से पतले दस्त और पेट में दर्द है, पर बुखार नहीं है।", "text_ref": "kal se patle dast aur pet mein dard hai par bukhar nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "ORS पीजिए और Ciprofloxacin मत लीजिए।", "text_ref": "ors pijiye aur ciprofloxacin mat lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "62315008", "preferred_term": "Diarrhea", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "21522001", "preferred_term": "Abdominal pain", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387077008", "preferred_term": "Oral rehydration salts", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "372840008", "preferred_term": "Ciprofloxacin", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "OPD-T14",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["laterality_right", "fractional_dose"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "तीन महीने से दाएं घुटने में दर्द है और कमर में दर्द भी है।", "text_ref": "teen mahine se daayein ghutne mein dard hai aur kamar mein dard bhi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Paracetamol डेढ़ गोली जरूरत पर लें, Diclofenac मत लीजिए।", "text_ref": "paracetamol dedh goli zaroorat par lein diclofenac mat lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "30989003", "preferred_term": "Knee pain", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "mo", "laterality": "right"},
                {"snomed_code": "161891005", "preferred_term": "Backache", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.5},
                {"snomed_code": "703125008", "preferred_term": "Diclofenac", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "OPD-T15",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["nausea", "constipation", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "छह दिन से कब्ज है और जी मचलाना रहता है, पर पीलिया नहीं है।", "text_ref": "chhah din se qabz hai aur ji machlana rehta hai par peeliya nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Ondansetron एक गोली सुबह लें और पानी ज्यादा पिएं।", "text_ref": "ondansetron ek goli subah lein aur pani zyada piyein"},
            ],
            "gold_annotations": [
                {"snomed_code": "14760008", "preferred_term": "Constipation", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 6.0, "duration_unit": "d"},
                {"snomed_code": "422587007", "preferred_term": "Nausea", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "18165001", "preferred_term": "Jaundice", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372487007", "preferred_term": "Ondansetron", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-T16",
            "split": "test",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["dysuria", "family_subject", "negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "चार दिन से पेशाब में जलन है, माताजी को diabetes है पर मुझे बुखार नहीं है।", "text_ref": "chaar din se peshab mein jalan hai mataji ko diabetes hai par mujhe bukhar nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Urine test कराइए और अभी antibiotic मत लीजिए।", "text_ref": "urine test karaiye aur abhi antibiotic mat lijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "49650001", "preferred_term": "Dysuria", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 4.0, "duration_unit": "d"},
                {"snomed_code": "44054006", "preferred_term": "Diabetes mellitus type 2", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "family_member"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },

        # ==================== DEV / CALIBRATION SPLIT (8 CONSULTS) ====================
        {
            "consult_id": "OPD-D01",
            "split": "dev",
            "domain": "acute_febrile_amr",
            "stress_tags": ["negation"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "दो दिन से बुखार और खांसी है, पर सांस फूलना नहीं है।", "text_ref": "do din se bukhar aur khansi hai par saans phoolna nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Paracetamol एक गोली लें।", "text_ref": "paracetamol ek goli lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "d"},
                {"snomed_code": "49727002", "preferred_term": "Cough", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "267036007", "preferred_term": "Dyspnea", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-D02",
            "split": "dev",
            "domain": "cardiometabolic",
            "stress_tags": ["fractional_dose"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "मेरा BP high है और सिर में दर्द है।", "text_ref": "mera bp high hai aur sir mein dard hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Amlodipine डेढ़ गोली सुबह लें।", "text_ref": "amlodipine dedh goli subah lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "38341003", "preferred_term": "Hypertensive disorder", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "25064002", "preferred_term": "Headache", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "386864001", "preferred_term": "Amlodipine", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.5},
            ],
        },
        {
            "consult_id": "OPD-D03",
            "split": "dev",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["idiom_gas"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "तीन दिन से पेट में गैस और सीने में जलन है।", "text_ref": "teen din se pet mein gas aur seene mein jalan hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Omeprazole एक गोली सुबह लें।", "text_ref": "omeprazole ek goli subah lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "162076009", "preferred_term": "Abdominal bloating", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "16331000", "preferred_term": "Heartburn", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "387137007", "preferred_term": "Omeprazole", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-D04",
            "split": "dev",
            "domain": "acute_febrile_amr",
            "stress_tags": ["amr_stewardship"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "तीन दिन से नाक बहना और गले में दर्द है।", "text_ref": "teen din se naak behna aur gale mein dard hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Cetirizine एक गोली लें, antibiotic मत लें।", "text_ref": "cetirizine ek goli lein antibiotic mat lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "64531003", "preferred_term": "Nasal discharge", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "162397003", "preferred_term": "Pain in throat", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "372887000", "preferred_term": "Cetirizine", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
                {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "OPD-D05",
            "split": "dev",
            "domain": "cardiometabolic",
            "stress_tags": ["hypoglycemia"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "आज सुबह शुगर कम हो गई और पसीना आना हुआ।", "text_ref": "aaj subah sugar low aur paseena aana hua"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Glimepiride आधी गोली कर दीजिए।", "text_ref": "glimepiride aadhi goli kar dijiye"},
            ],
            "gold_annotations": [
                {"snomed_code": "302866003", "preferred_term": "Hypoglycemia", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "52613005", "preferred_term": "Excessive sweating", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "373492002", "preferred_term": "Glimepiride", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 0.5},
            ],
        },
        {
            "consult_id": "OPD-D06",
            "split": "dev",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["neck_pain"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "पांच दिन से गर्दन में दर्द है पर सुन्नपन नहीं है।", "text_ref": "paanch din se gardan mein dard hai par sunnapan nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Paracetamol एक गोली लें।", "text_ref": "paracetamol ek goli lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "81680005", "preferred_term": "Neck pain", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 5.0, "duration_unit": "d"},
                {"snomed_code": "44077006", "preferred_term": "Numbness", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-D07",
            "split": "dev",
            "domain": "acute_febrile_amr",
            "stress_tags": ["asthma"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-SwaraNeural", "text_tts": "मुझे दमा है और दो दिन से सांस फूलना बढ़ गया है, पर बुखार नहीं है।", "text_ref": "mujhe dama hai aur do din se saans phoolna badh gaya hai par bukhar nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-PrabhatNeural", "text_tts": "Salbutamol लीजिए और Montelukast एक गोली रात को लें।", "text_ref": "salbutamol lijiye aur montelukast ek goli raat ko lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "195967001", "preferred_term": "Asthma", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "267036007", "preferred_term": "Dyspnea", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "d"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387475002", "preferred_term": "Salbutamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "372729009", "preferred_term": "Montelukast", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
        {
            "consult_id": "OPD-D08",
            "split": "dev",
            "domain": "gi_musculoskeletal",
            "stress_tags": ["pruritus"],
            "turns": [
                {"speaker": "patient", "voice": "hi-IN-MadhurNeural", "text_tts": "तीन दिन से खुजली और लाल दाने हैं, पर बुखार नहीं है।", "text_ref": "teen din se khujli aur lal daane hai par bukhar nahi hai"},
                {"speaker": "doctor", "voice": "en-IN-NeerjaNeural", "text_tts": "Cetirizine एक गोली रात को लें।", "text_ref": "cetirizine ek goli raat ko lein"},
            ],
            "gold_annotations": [
                {"snomed_code": "418290006", "preferred_term": "Itching", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "271807003", "preferred_term": "Eruption of skin", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "372887000", "preferred_term": "Cetirizine", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.0},
            ],
        },
    ]
    return consults


def build_longitudinal_trajectories() -> List[Dict[str, object]]:
    """Build 3 Synthea-style multi-visit synthetic patients (3 sequential OPD visits each = 9 encounters)."""
    return [
        {
            "patient_id": "SYN-PAT-001",
            "persona": "54yo Male — Uncontrolled Type 2 Diabetes progressing to Neuropathy with Metformin titration",
            "visits": [
                {
                    "consult_id": "LONG-P1-V1",
                    "visit_date": "2026-08-10",
                    "transcript": "doctor sahab mujhe diabetes hai aur baar baar peshab aata hai metformin ek goli subah shaam le raha hoon",
                },
                {
                    "consult_id": "LONG-P1-V2",
                    "visit_date": "2026-09-22",
                    "transcript": "ab baar baar peshab nahi hai par sugar high hai aur chakkar aana hota hai metformin dedh goli subah shaam kar dijiye",
                },
                {
                    "consult_id": "LONG-P1-V3",
                    "visit_date": "2026-11-05",
                    "transcript": "sugar high abhi bhi hai aur do hafte se paer mein jhanjhanahat shuru ho gayi hai metformin do goli aur vitamin b12 ek goli roz lijiye",
                },
            ],
        },
        {
            "patient_id": "SYN-PAT-002",
            "persona": "46yo Female — Hypertension + NSAID-induced Gastritis resolved after stopping Ibuprofen",
            "visits": [
                {
                    "consult_id": "LONG-P2-V1",
                    "visit_date": "2026-09-01",
                    "transcript": "mera bp high rehta hai aur ghutne mein dard hai amlodipine ek goli aur ibuprofen ek goli le rahi hoon",
                },
                {
                    "consult_id": "LONG-P2-V2",
                    "visit_date": "2026-10-04",
                    "transcript": "bp high theek nahi hua amlodipine dedh goli karein aur pet mein gas banti hai aur seene mein jalan hai ibuprofen mat lijiye pantoprazole ek goli subah lein",
                },
                {
                    "consult_id": "LONG-P2-V3",
                    "visit_date": "2026-11-10",
                    "transcript": "ab seene mein jalan nahi hai aur pet mein gas nahi hai amlodipine dedh goli jaari rakhein",
                },
            ],
        },
        {
            "patient_id": "SYN-PAT-003",
            "persona": "29yo Male — Acute Viral URI evolving to secondary bacterial cough vs resolved fever",
            "visits": [
                {
                    "consult_id": "LONG-P3-V1",
                    "visit_date": "2026-10-25",
                    "transcript": "teen din se bukhar aur sukhi khansi hai paracetamol ek goli lijiye antibiotic mat lijiye",
                },
                {
                    "consult_id": "LONG-P3-V2",
                    "visit_date": "2026-11-02",
                    "transcript": "bukhar nahi hai par balgam wali khansi aur saans phoolna hai amoxicillin ek goli subah shaam lijiye",
                },
                {
                    "consult_id": "LONG-P3-V3",
                    "visit_date": "2026-11-12",
                    "transcript": "ab balgam wali khansi nahi hai aur saans phoolna nahi hai amoxicillin mat lijiye",
                },
            ],
        },
    ]


def build_kannada_portability_consults() -> List[Dict[str, object]]:
    """Build 5 Kannada OPD test consults proving zero-core-code-change Karnataka readiness."""
    return [
        {
            "consult_id": "KN-OPD-01",
            "language": "kn-IN",
            "voice": "kn-IN-SapnaNeural",
            "text_tts": "ಡಾಕ್ಟರ್ ನನಗೆ ಮೂರು ದಿನದಿಂದ ಜ್ವರ ಇದೆ ಆದರೆ ತಲೆನೋವು ಇಲ್ಲ ಪ್ಯಾರಾಸಿಟಮಾಲ್ ಒಂದೂವರೆ ಮಾತ್ರೆ",
            "text_ref": "doctor nanage mooru dinadinda jvara ide aadare talenovu illa paracetamol onduvare maatre",
            "gold_annotations": [
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 3.0, "duration_unit": "d"},
                {"snomed_code": "25064002", "preferred_term": "Headache", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "387517004", "preferred_term": "Paracetamol", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 1.5},
            ],
        },
        {
            "consult_id": "KN-OPD-02",
            "language": "kn-IN",
            "voice": "kn-IN-GaganNeural",
            "text_tts": "ನನಗೆ ಕೆಮ್ಮು ಮತ್ತು ಶೀತ ಇದೆ ಆದರೆ ಜ್ವರ ಇಲ್ಲ ಆಂಟಿಬಯೋಟಿಕ್ ಬೇಡ",
            "text_ref": "nanage kemmu mattu sheeta ide aadare jvara illa antibiotic beda",
            "gold_annotations": [
                {"snomed_code": "49727002", "preferred_term": "Cough", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "82272006", "preferred_term": "Common cold", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
                {"snomed_code": "255631004", "preferred_term": "Antibiotic", "semantic_tag": "medication", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "KN-OPD-03",
            "language": "kn-IN",
            "voice": "kn-IN-SapnaNeural",
            "text_tts": "ನನಗೆ ಸಕ್ಕರೆ ಕಾಯಿಲೆ ಮತ್ತು ತಲೆಸುತ್ತು ಇದೆ ಮೆಟ್ಫಾರ್ಮಿನ್ ಎರಡು ಮಾತ್ರೆ",
            "text_ref": "nanage sakkare kaayile mattu talesuttu ide metformin eradu maatre",
            "gold_annotations": [
                {"snomed_code": "44054006", "preferred_term": "Diabetes mellitus type 2", "semantic_tag": "disorder", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "404640003", "preferred_term": "Dizziness", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "372567009", "preferred_term": "Metformin", "semantic_tag": "medication", "polarity": "affirmed", "subject": "patient", "dose_value": 2.0},
            ],
        },
        {
            "consult_id": "KN-OPD-04",
            "language": "kn-IN",
            "voice": "kn-IN-GaganNeural",
            "text_tts": "ನನಗೆ ಹೊಟ್ಟೆ ಉಬ್ಬರ ಮತ್ತು ಎದೆ ಉರಿ ಇದೆ ಆದರೆ ವಾಂತಿ ಇಲ್ಲ",
            "text_ref": "nanage hotte ubbara mattu ede uri ide aadare vaanti illa",
            "gold_annotations": [
                {"snomed_code": "162076009", "preferred_term": "Abdominal bloating", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "16331000", "preferred_term": "Heartburn", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient"},
                {"snomed_code": "422400008", "preferred_term": "Vomiting", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
            ],
        },
        {
            "consult_id": "KN-OPD-05",
            "language": "kn-IN",
            "voice": "kn-IN-SapnaNeural",
            "text_tts": "ನನಗೆ ಎರಡು ದಿನದಿಂದ ಭೇದಿ ಇದೆ ಆದರೆ ಜ್ವರ ಇಲ್ಲ",
            "text_ref": "nanage eradu dinadinda bhedi ide aadare jvara illa",
            "gold_annotations": [
                {"snomed_code": "62315008", "preferred_term": "Diarrhea", "semantic_tag": "finding", "polarity": "affirmed", "subject": "patient", "duration_value": 2.0, "duration_unit": "d"},
                {"snomed_code": "386661006", "preferred_term": "Fever", "semantic_tag": "finding", "polarity": "negated", "subject": "patient"},
            ],
        },
    ]


def main() -> None:
    LEXICON_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    hi_lex = build_hinglish_lexicon()
    kn_lex = build_kannada_lexicon()
    consults = build_pilot_consults()
    longitudinal = build_longitudinal_trajectories()
    kannada = build_kannada_portability_consults()

    (LEXICON_DIR / "hinglish_snomed_lexicon.json").write_text(
        json.dumps(hi_lex, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (LEXICON_DIR / "kannada_snomed_lexicon.json").write_text(
        json.dumps(kn_lex, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (MANIFEST_DIR / "pilot_consults_v1.json").write_text(
        json.dumps({"version": "1.0", "consults": consults}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (MANIFEST_DIR / "longitudinal_patients_v1.json").write_text(
        json.dumps({"version": "1.0", "patients": longitudinal}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (MANIFEST_DIR / "kannada_portability_v1.json").write_text(
        json.dumps({"version": "1.0", "consults": kannada}, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Wrote Hinglish lexicon: {hi_lex['num_concepts']} SNOMED CT concepts")
    print(f"Wrote Kannada lexicon plugin: {kn_lex['num_concepts']} SNOMED CT concepts")
    print(f"Wrote Hinglish OPD consults: {len(consults)} ({sum(c['split']=='test' for c in consults)} test, {sum(c['split']=='dev' for c in consults)} dev)")
    print(f"Wrote Longitudinal patient trajectories: {len(longitudinal)} patients ({sum(len(p['visits']) for p in longitudinal)} visits)")
    print(f"Wrote Kannada portability consults: {len(kannada)}")


if __name__ == "__main__":
    main()
