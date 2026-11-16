"""AWS Transcribe Hinglish adapter & Cloud Cost Governance calculator (Lecture 9 Slides 11-12)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


# AWS Mumbai Region (ap-south-1) on-demand pricing as of 2026
AWS_TRANSCRIBE_STANDARD_USD_PER_MIN = 0.024
AWS_TRANSCRIBE_MEDICAL_USD_PER_MIN = 0.075  # Note: Medical is English-only; multi-lang uses Standard
AWS_S3_AP_SOUTH_1_USD_PER_GB_MONTH = 0.025
BEDROCK_HAIKU_INPUT_USD_PER_1K_TOK = 0.00025
BEDROCK_HAIKU_OUTPUT_USD_PER_1K_TOK = 0.00125


@dataclass
class CloudCostEstimate:
    """Bounded cloud cost projection obeying Prof. Sethi's no-unapproved-GPU rule."""

    scenario_name: str
    num_consults: int
    avg_consult_minutes: float
    total_audio_minutes: float
    aws_transcribe_passes: int
    transcribe_cost_usd: float
    s3_storage_cost_usd: float
    constrained_llm_cost_usd: float
    ec2_gpu_instances_used: int
    total_estimated_usd: float
    region: str = "ap-south-1"
    within_budget_cap: bool = True


def estimate_project_cloud_budget(
    num_consults: int = 200,
    avg_consult_minutes: float = 2.0,
    aws_transcribe_passes: int = 2,
    budget_cap_usd: float = 25.0,
) -> CloudCostEstimate:
    """Compute transparent AWS spend for dataset evaluation + full-scale 200-consult benchmark."""
    total_mins = num_consults * avg_consult_minutes
    # Minimum billable increment on AWS Transcribe is 15 seconds, modeled conservatively
    transcribe_usd = total_mins * aws_transcribe_passes * AWS_TRANSCRIBE_STANDARD_USD_PER_MIN
    # 16kHz 16-bit mono WAV = ~1.92 MB/min -> <1 GB total in S3 ap-south-1
    audio_gb = (total_mins * 1.92) / 1024.0
    s3_usd = max(0.02, audio_gb * AWS_S3_AP_SOUTH_1_USD_PER_GB_MONTH)
    # Constrained candidate reranking (~600 input + ~200 output tokens per consult)
    llm_usd = num_consults * (
        0.6 * BEDROCK_HAIKU_INPUT_USD_PER_1K_TOK + 0.2 * BEDROCK_HAIKU_OUTPUT_USD_PER_1K_TOK
    )
    total_usd = transcribe_usd + s3_usd + llm_usd
    return CloudCostEstimate(
        scenario_name=f"{num_consults}-Consult Hinglish Benchmark ({aws_transcribe_passes}x AWS Transcribe + Local Open ASR)",
        num_consults=num_consults,
        avg_consult_minutes=avg_consult_minutes,
        total_audio_minutes=round(total_mins, 2),
        aws_transcribe_passes=aws_transcribe_passes,
        transcribe_cost_usd=round(transcribe_usd, 3),
        s3_storage_cost_usd=round(s3_usd, 3),
        constrained_llm_cost_usd=round(llm_usd, 3),
        ec2_gpu_instances_used=0,
        total_estimated_usd=round(total_usd, 2),
        region="ap-south-1",
        within_budget_cap=(total_usd <= budget_cap_usd),
    )


def build_aws_transcribe_job_payload(
    job_name: str,
    s3_audio_uri: str,
    max_speakers: int = 3,
    region: str = "ap-south-1",
) -> Dict[str, object]:
    """Build India-region compliant AWS Transcribe multi-language (`hi-IN` + `en-IN`) job config."""
    if region != "ap-south-1":
        raise ValueError(
            f"Data residency violation: expected region 'ap-south-1' (Mumbai), got '{region}'."
        )
    return {
        "TranscriptionJobName": job_name,
        "Media": {"MediaFileUri": s3_audio_uri},
        "IdentifyMultipleLanguages": True,
        "LanguageOptions": ["hi-IN", "en-IN"],
        "Settings": {
            "ShowSpeakerLabels": True,
            "MaxSpeakerLabels": max_speakers,
            "ShowAlternatives": True,
            "MaxAlternatives": 3,
        },
        "Tags": [
            {"Key": "Course", "Value": "ComputingForMedicine2026"},
            {"Key": "Project", "Value": "HinglishOPDScribe"},
            {"Key": "DataClassification", "Value": "SyntheticConsentedOnly"},
            {"Key": "AutoCleanup", "Value": "true"},
        ],
    }


def generate_governance_summary() -> Dict[str, object]:
    """Generate complete AWS cost & resource inventory report for midsem & endsem scales."""
    midsem_actual = CloudCostEstimate(
        scenario_name="Mid-Semester Pilot Execution (Apple M4 Local Compute Only)",
        num_consults=30,
        avg_consult_minutes=0.45,
        total_audio_minutes=13.5,
        aws_transcribe_passes=0,
        transcribe_cost_usd=0.0,
        s3_storage_cost_usd=0.0,
        constrained_llm_cost_usd=0.0,
        ec2_gpu_instances_used=0,
        total_estimated_usd=0.0,
        region="local-apple-m4",
        within_budget_cap=True,
    )
    endsem_150 = estimate_project_cloud_budget(num_consults=150, avg_consult_minutes=2.0, aws_transcribe_passes=1)
    endsem_200_2pass = estimate_project_cloud_budget(num_consults=200, avg_consult_minutes=2.0, aws_transcribe_passes=2)
    summaries: List[Dict[str, object]] = [
        asdict(midsem_actual),
        asdict(endsem_150),
        asdict(endsem_200_2pass),
    ]
    return {
        "gpu_policy": "STRICT_ZERO_UNAPPROVED_CLOUD_GPUS",
        "storage_residency": "ap-south-1 (Mumbai) with lifecycle auto-delete <= 14 days",
        "scenarios": summaries,
    }
