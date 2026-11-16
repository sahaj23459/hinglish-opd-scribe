"""HL7 FHIR R4 Bundle builder (Patient, Encounter, Condition, Observation, MedicationStatement, FamilyMemberHistory)."""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.linking.concept_linker import LinkedMention


SNOMED_SYSTEM_URI = "http://snomed.info/sct"

LATERALITY_SNOMED = {
    "left": ("7771000", "Left"),
    "right": ("24028007", "Right"),
    "bilateral": ("51440002", "Right and left"),
}


def build_fhir_r4_bundle(
    consult_id: str,
    patient_id: str,
    visit_date: str,
    mentions: List[LinkedMention],
    visit_number: int = 1,
) -> Dict[str, object]:
    """Serialize linked Hinglish clinical mentions into an ABDM-aligned HL7 FHIR R4 Bundle."""
    entries: List[Dict[str, object]] = []

    patient_ref = f"Patient/{patient_id}"
    encounter_id = f"enc-{consult_id}"
    encounter_ref = f"Encounter/{encounter_id}"

    # 1. Patient Resource
    entries.append(
        {
            "fullUrl": f"urn:uuid:patient-{patient_id}",
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "meta": {
                    "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"],
                    "security": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                            "code": "HTEST",
                            "display": "test health data (synthetic consented)",
                        }
                    ],
                },
                "active": True,
            },
        }
    )

    # 2. Encounter Resource
    entries.append(
        {
            "fullUrl": f"urn:uuid:{encounter_id}",
            "resource": {
                "resourceType": "Encounter",
                "id": encounter_id,
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory",
                },
                "subject": {"reference": patient_ref},
                "period": {"start": visit_date, "end": visit_date},
                "extension": [
                    {
                        "url": "https://hinglish-scribe.example.org/fhir/StructureDefinition/visit-sequence",
                        "valueInteger": visit_number,
                    }
                ],
            },
        }
    )

    # 3. Clinical Resources per Validated SNOMED Mention
    for idx, m in enumerate(mentions, start=1):
        if not m.is_valid_snomed_in_lexicon:
            continue

        at = m.attributes
        provenance_ext = {
            "url": "https://hinglish-scribe.example.org/fhir/StructureDefinition/transcript-span",
            "extension": [
                {"url": "matchedText", "valueString": m.matched_span},
                {"url": "charStart", "valueInteger": m.span_start},
                {"url": "charEnd", "valueInteger": m.span_end},
                {"url": "confidence", "valueDecimal": m.confidence},
            ],
        }

        if m.semantic_tag == "medication":
            status = "not-taken" if at.polarity == "negated" else "active"
            med_res: Dict[str, object] = {
                "resourceType": "MedicationStatement",
                "id": f"med-{consult_id}-{idx}",
                "status": status,
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system": SNOMED_SYSTEM_URI,
                            "code": m.snomed_code,
                            "display": m.preferred_term,
                        }
                    ],
                    "text": m.preferred_term,
                },
                "subject": {"reference": patient_ref},
                "context": {"reference": encounter_ref},
                "effectiveDateTime": visit_date,
                "extension": [provenance_ext],
            }
            dosage_entry: Dict[str, object] = {}
            if at.dose_value is not None:
                dosage_entry["doseAndRate"] = [
                    {
                        "doseQuantity": {
                            "value": at.dose_value,
                            "unit": at.dose_unit or "tablet",
                            "system": "http://unitsofmeasure.org",
                            "code": "{tbl}" if (at.dose_unit or "tablet") == "tablet" else "mL",
                        }
                    }
                ]
            if at.frequency_code:
                dosage_entry["timing"] = {"code": {"text": at.frequency_code}}
            if at.strength_mg is not None:
                dosage_entry["text"] = f"{int(at.strength_mg)} mg"
            if dosage_entry:
                med_res["dosage"] = [dosage_entry]

            entries.append({"fullUrl": f"urn:uuid:med-{consult_id}-{idx}", "resource": med_res})

        elif at.subject == "family_member":
            fam_res: Dict[str, object] = {
                "resourceType": "FamilyMemberHistory",
                "id": f"fam-{consult_id}-{idx}",
                "status": "completed",
                "patient": {"reference": patient_ref},
                "date": visit_date,
                "relationship": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": "FAMMEMB",
                            "display": "family member",
                        }
                    ]
                },
                "condition": [
                    {
                        "code": {
                            "coding": [
                                {
                                    "system": SNOMED_SYSTEM_URI,
                                    "code": m.snomed_code,
                                    "display": m.preferred_term,
                                }
                            ]
                        }
                    }
                ],
                "extension": [provenance_ext],
            }
            entries.append({"fullUrl": f"urn:uuid:fam-{consult_id}-{idx}", "resource": fam_res})

        else:
            if at.polarity == "negated":
                ver_code = "refuted"
            elif m.needs_doctor_confirmation:
                ver_code = "provisional"
            else:
                ver_code = "confirmed"

            cond_res: Dict[str, object] = {
                "resourceType": "Condition",
                "id": f"cond-{consult_id}-{idx}",
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "inactive" if ver_code == "refuted" else "active",
                        }
                    ]
                },
                "verificationStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            "code": ver_code,
                        }
                    ]
                },
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                "code": "encounter-diagnosis" if m.semantic_tag == "disorder" else "problem-list-item",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": SNOMED_SYSTEM_URI,
                            "code": m.snomed_code,
                            "display": m.preferred_term,
                        }
                    ],
                    "text": m.preferred_term,
                },
                "subject": {"reference": patient_ref},
                "encounter": {"reference": encounter_ref},
                "recordedDate": visit_date,
                "extension": [provenance_ext],
            }
            if at.laterality in LATERALITY_SNOMED:
                lat_code, lat_disp = LATERALITY_SNOMED[at.laterality]
                cond_res["bodySite"] = [
                    {
                        "coding": [
                            {
                                "system": SNOMED_SYSTEM_URI,
                                "code": lat_code,
                                "display": lat_disp,
                            }
                        ]
                    }
                ]
            entries.append({"fullUrl": f"urn:uuid:cond-{consult_id}-{idx}", "resource": cond_res})

            # Emit companion Observation when structured symptom duration is present
            if at.duration_value is not None and at.duration_unit:
                obs_res: Dict[str, object] = {
                    "resourceType": "Observation",
                    "id": f"obs-dur-{consult_id}-{idx}",
                    "status": "preliminary" if m.needs_doctor_confirmation else "final",
                    "code": {
                        "coding": [
                            {
                                "system": SNOMED_SYSTEM_URI,
                                "code": "103335007",
                                "display": "Duration of clinical finding",
                            }
                        ],
                        "text": f"Duration of {m.preferred_term}",
                    },
                    "subject": {"reference": patient_ref},
                    "encounter": {"reference": encounter_ref},
                    "focus": [{"reference": f"Condition/cond-{consult_id}-{idx}"}],
                    "effectiveDateTime": visit_date,
                    "valueQuantity": {
                        "value": at.duration_value,
                        "unit": at.duration_unit,
                        "system": "http://unitsofmeasure.org",
                        "code": at.duration_unit,
                    },
                }
                entries.append({"fullUrl": f"urn:uuid:obs-dur-{consult_id}-{idx}", "resource": obs_res})

    return {
        "resourceType": "Bundle",
        "id": f"bundle-{consult_id}",
        "type": "collection",
        "timestamp": f"{visit_date}T10:30:00+05:30",
        "entry": entries,
    }


def validate_fhir_bundle_schema(bundle: Dict[str, object]) -> Tuple[bool, List[str]]:
    """Validate core HL7 FHIR R4 structural invariants & SNOMED coding presence."""
    errors: List[str] = []
    if bundle.get("resourceType") != "Bundle":
        errors.append("Root resourceType must be 'Bundle'.")
    if bundle.get("type") not in ("collection", "transaction", "document"):
        errors.append("Invalid Bundle.type.")
    entries = bundle.get("entry")
    if not isinstance(entries, list) or len(entries) < 2:
        errors.append("Bundle must contain at least Patient and Encounter entries.")
        return False, errors

    allowed_types = {
        "Patient",
        "Encounter",
        "Condition",
        "Observation",
        "MedicationStatement",
        "FamilyMemberHistory",
    }
    for idx, ent in enumerate(entries):
        res = ent.get("resource", {}) if isinstance(ent, dict) else {}
        rtype = res.get("resourceType")
        if rtype not in allowed_types:
            errors.append(f"Entry {idx} has unexpected resourceType '{rtype}'.")
        if rtype == "Condition":
            codings = res.get("code", {}).get("coding", [])
            if not codings or codings[0].get("system") != SNOMED_SYSTEM_URI or not codings[0].get("code"):
                errors.append(f"Condition {res.get('id')} missing SNOMED CT coding.")
        elif rtype == "MedicationStatement":
            codings = res.get("medicationCodeableConcept", {}).get("coding", [])
            if not codings or codings[0].get("system") != SNOMED_SYSTEM_URI or not codings[0].get("code"):
                errors.append(f"MedicationStatement {res.get('id')} missing SNOMED CT coding.")

    return (len(errors) == 0), errors
