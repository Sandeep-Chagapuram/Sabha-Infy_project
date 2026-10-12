from typing import Dict, Any, List

SAMPLE_A_PRODUCT_LAUNCH = """[00:01:10] Priya: Welcome everyone. Today we must lock down the v1.0 Product Launch plan for next month.
[00:01:25] Rahul: The core microservices are stable, but the payment gateway webhook needs end-to-end load testing.
[00:01:42] Vikram: I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday.
[00:02:00] Priya: Excellent commitment, Vikram. What about the mobile push notifications?
[00:02:15] Neha: We should consider delaying iOS push notifications to v1.1. It might take another two weeks.
[00:02:32] Priya: Let's officially decide: we launch web and android first on November 15th, and defer iOS push notifications to v1.1. Everyone agreed?
[00:02:48] Rahul: Agreed. Confirmed.
[00:03:02] Neha: Agreed. That reduces critical path risk.
[00:03:15] Vikram: One open question: who is handling the compliance sign-off for EU GDPR data export? We haven't assigned an owner for that yet.
[00:03:30] Priya: Good catch. Let's leave EU compliance sign-off unassigned for now until legal responds by Monday."""

SAMPLE_B_PROJECT_AT_RISK = """[00:00:45] Amit: Team, our database migration to Aurora PostgreSQL is at high risk.
[00:01:05] Sneha: The data engineering team in Singapore promised schema parity by yesterday, but they are completely unresponsive.
[00:01:22] Rohan: I previously said I could finish the migration script by tomorrow, but actually I cannot proceed because their table partitioning is completely missing.
[00:01:40] Amit: So we are hard-blocked on the Singapore team's schema?
[00:01:52] Rohan: Yes, exactly. Without their partitioning DDL, running the migration will cause prolonged table locks and customer downtime.
[00:02:10] Sneha: The unrealistic deadline of Friday is impossible now. If we push ahead without verification, we risk massive data corruption.
[00:02:30] Amit: We also made an unverified assumption that our read-replicas could handle 15,000 queries per second without connection pooling.
[00:02:50] Rohan: We need someone to escalate directly to the Singapore VP of Engineering today. I cannot do it due to client commitments."""

SAMPLE_C_CREATIVE_PROBLEM_SOLVING = """[00:00:30] Ananya: We have a major scaling bottleneck: our transcription audio processing server costs have surged to $18,000 a month.
[00:00:50] Dev: Our budget cap for this quarter is strictly $5,000 per month. We need alternative architectural approaches immediately.
[00:01:15] Kartik: Approach one: We could move audio silence detection and compression directly to the client browser using WebAssembly.
[00:01:35] Ananya: Benefit is near-zero server CPU cost for silence, but limitation is older Android browsers might struggle with WASM threads.
[00:01:55] Dev: Approach two: What if we route audio through an on-premise Qualcomm Cloud AI hardware accelerator instance rather than general cloud CPUs?
[00:02:18] Kartik: That could yield a 4x throughput improvement per watt, but requires testing model weight quantization.
[00:02:38] Dev: Approach three: Implement adaptive sample rate reduction during background pauses.
[00:02:55] Ananya: We also have a research question: what are the benchmark latency and cost differences between Qualcomm Cloud AI inference versus traditional cloud GPUs for real-time speech?"""

DEMO_SAMPLES_CATALOG = {
    "sample_a": {
        "id": "sample_a",
        "title": "Product Launch Readiness & Scope Lock",
        "category": "Product Launch",
        "description": "Demonstrates explicit commitments, agreed launch decision, deferred feature, unassigned compliance task, and relative deadlines.",
        "transcript": SAMPLE_A_PRODUCT_LAUNCH,
        "meeting_date": "2026-10-15T10:00:00Z",
        "timezone": "Asia/Kolkata",
        "participants": ["Priya", "Rahul", "Vikram", "Neha"],
        "project_context": "v1.0 Launch Planning Sprint"
    },
    "sample_b": {
        "id": "sample_b",
        "title": "Database Migration Risk & Blocker Review",
        "category": "Project at Risk",
        "description": "Demonstrates withdrawn commitment, cross-team hard blocker, unrealistic deadline alert, missing task owner, and unverified assumptions.",
        "transcript": SAMPLE_B_PROJECT_AT_RISK,
        "meeting_date": "2026-10-18T14:30:00Z",
        "timezone": "Asia/Kolkata",
        "participants": ["Amit", "Sneha", "Rohan"],
        "project_context": "Aurora PostgreSQL Core Migration"
    },
    "sample_c": {
        "id": "sample_c",
        "title": "Audio Processing Architecture & Cost Reduction",
        "category": "Creative Problem Solving",
        "description": "Demonstrates 3 distinct architectural alternatives, trade-off analysis, hard budget constraints ($5k cap), and verifiable research questions.",
        "transcript": SAMPLE_C_CREATIVE_PROBLEM_SOLVING,
        "meeting_date": "2026-10-20T16:00:00Z",
        "timezone": "Asia/Kolkata",
        "participants": ["Ananya", "Dev", "Kartik"],
        "project_context": "Infrastructure Cost Optimization"
    }
}

# Pre-calculated, strictly grounded demo intelligence records
# Used ONLY in explicit Demo Mode when QUALCOMM_API_KEY is not configured by user.
# Clearly labelled with provenance and disclaimer.
DEMO_ANALYSIS_CACHE = {
    "sample_a": {
        "executive_summary": "The team reviewed the v1.0 Product Launch. Confirmed decisions were made to launch Web and Android first on November 15th while deferring iOS push notifications to v1.1. Vikram committed to payment gateway load testing by Friday. EU GDPR compliance sign-off remains unassigned pending legal clarification.",
        "tasks": [
            {
                "title": "Execute end-to-end payment gateway load testing and share benchmark report",
                "assignee_name": "Vikram",
                "is_ownership_confirmed": True,
                "deadline_text": "by this Friday",
                "deadline_confidence": "explicit",
                "priority": "high",
                "status": "pending",
                "source_evidence_quote": "I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday.",
                "validation_status": "explicitly_stated"
            },
            {
                "title": "EU GDPR data export compliance sign-off",
                "assignee_name": None,  # Explicitly unassigned as required!
                "is_ownership_confirmed": False,
                "deadline_text": "by Monday",
                "deadline_confidence": "ambiguous",
                "priority": "medium",
                "status": "pending",
                "source_evidence_quote": "who is handling the compliance sign-off for EU GDPR data export? We haven't assigned an owner for that yet.",
                "validation_status": "evidence_supported"
            }
        ],
        "decisions": [
            {
                "title": "Launch Web and Android on November 15th; Defer iOS push notifications",
                "description": "Agreed by Priya, Rahul, and Neha to minimize critical path risks for initial release.",
                "status": "confirmed",
                "source_evidence_quote": "we launch web and android first on November 15th, and defer iOS push notifications to v1.1."
            }
        ],
        "risks": [
            {
                "title": "EU GDPR compliance ownership void",
                "description": "No team member owns GDPR sign-off prior to the scheduled November 15 launch date.",
                "severity": "high",
                "potential_impact": "Legal non-compliance block preventing European customer onboarding.",
                "suggested_mitigation": "Designate a compliance lead immediately following legal feedback on Monday.",
                "source_evidence_quote": "who is handling the compliance sign-off for EU GDPR data export? We haven't assigned an owner for that yet."
            }
        ],
        "second_brain": {
            "what_we_believe": [
                {
                    "item": "Launch target date of November 15th is confirmed for Web and Android.",
                    "type": "decision",
                    "evidence_quote": "we launch web and android first on November 15th, and defer iOS push notifications to v1.1."
                },
                {
                    "item": "Vikram owns payment gateway webhook load testing due Friday.",
                    "type": "commitment",
                    "evidence_quote": "I will handle the end-to-end payment gateway load testing and share the benchmark report by this Friday."
                }
            ],
            "what_we_might_be_missing": [
                {
                    "finding": "EU GDPR export sign-off lacks clear ownership and legal SLA.",
                    "concern_type": "missing_ownership",
                    "evidence_quote": "We haven't assigned an owner for that yet.",
                    "reasoning": "Launching without verified GDPR compliance exposes organization to European regulatory fines.",
                    "potential_impact": "Delayed release or regulatory penalties.",
                    "confidence": "high",
                    "suggested_verification": "Confirm status of legal team response on Monday morning."
                }
            ],
            "what_to_investigate_next": [
                {
                    "recommendation": "Confirm whether payment gateway load test covers 3D Secure fallback scenarios.",
                    "action_type": "validation",
                    "suggested_owner": "Vikram",
                    "rationale": "High-traffic spikes often cause 3DS timeouts if third-party ACS servers throttle."
                }
            ]
        }
    },
    "sample_b": {
        "executive_summary": "Aurora PostgreSQL database migration is critically blocked by the Singapore data engineering team's missing schema partitioning DDL. Rohan explicitly withdrew his earlier commitment to complete the migration script. The Friday deadline was declared impossible. An unverified assumption regarding read-replica connection capacity was flagged.",
        "tasks": [
            {
                "title": "Escalate schema parity blockage to Singapore VP of Engineering",
                "assignee_name": None,  # Explicitly unassigned!
                "is_ownership_confirmed": False,
                "deadline_text": "today",
                "deadline_confidence": "explicit",
                "priority": "urgent",
                "status": "blocked",
                "blocker_reason": "Rohan cannot do it due to client commitments; awaits assigned escalation owner.",
                "source_evidence_quote": "We need someone to escalate directly to the Singapore VP of Engineering today. I cannot do it due to client commitments.",
                "validation_status": "explicitly_stated"
            }
        ],
        "decisions": [
            {
                "title": "Halt Aurora migration execution until schema partitioning is provided",
                "description": "Prevent customer downtime and table locking caused by running migration without partitioning DDL.",
                "status": "confirmed",
                "source_evidence_quote": "Without their partitioning DDL, running the migration will cause prolonged table locks and customer downtime."
            }
        ],
        "risks": [
            {
                "title": "Customer downtime from premature migration run",
                "description": "Running unpartitioned database migration will trigger severe database locks.",
                "severity": "critical",
                "potential_impact": "Multi-hour production outage and potential data corruption.",
                "suggested_mitigation": "Hold migration until Singapore team delivers partitioning DDL.",
                "source_evidence_quote": "Without their partitioning DDL, running the migration will cause prolonged table locks and customer downtime."
            },
            {
                "title": "Unverified read-replica query capacity (15k QPS)",
                "description": "Assumption that read-replicas handle 15k QPS without connection pooling is unvalidated.",
                "severity": "high",
                "potential_impact": "Connection pool exhaustion under peak customer traffic.",
                "suggested_mitigation": "Perform simulated connection load test on staging replica.",
                "source_evidence_quote": "We also made an unverified assumption that our read-replicas could handle 15,000 queries per second without connection pooling."
            }
        ],
        "second_brain": {
            "what_we_believe": [
                {
                    "item": "Aurora migration cannot proceed without partitioning DDL.",
                    "type": "constraint",
                    "evidence_quote": "Without their partitioning DDL, running the migration will cause prolonged table locks and customer downtime."
                }
            ],
            "what_we_might_be_missing": [
                {
                    "finding": "Rohan's withdrawn commitment leaves script development stalled with no replacement.",
                    "concern_type": "withdrawn_commitment",
                    "evidence_quote": "I previously said I could finish the migration script by tomorrow, but actually I cannot proceed",
                    "reasoning": "Even if Singapore provides DDL, script execution requires designated engineering hours.",
                    "potential_impact": "Prolonged sprint delay.",
                    "confidence": "high",
                    "suggested_verification": "Review team sprint capacity to allocate backup engineer."
                }
            ],
            "what_to_investigate_next": [
                {
                    "recommendation": "Set up PgBouncer connection pooling benchmark for read-replicas.",
                    "action_type": "experiment",
                    "suggested_owner": "Amit",
                    "rationale": "Direct PostgreSQL connections will saturate CPU at 15k QPS without pooling."
                }
            ]
        }
    },
    "sample_c": {
        "executive_summary": "The team addressed a critical infrastructure cost overrun ($18,000/month vs $5,000/month budget cap). Three distinct architectural solutions were formulated: Browser WebAssembly silence filtering, Qualcomm Cloud AI dedicated hardware inference, and adaptive sample rate reduction. A research spike was defined to benchmark Qualcomm throughput per watt.",
        "tasks": [
            {
                "title": "Benchmark Qualcomm Cloud AI inference throughput per watt and model weight quantization",
                "assignee_name": "Dev",
                "is_ownership_confirmed": True,
                "deadline_text": "unspecified",
                "deadline_confidence": "unspecified",
                "priority": "high",
                "status": "in_progress",
                "source_evidence_quote": "What if we route audio through an on-premise Qualcomm Cloud AI hardware accelerator instance rather than general cloud CPUs?",
                "validation_status": "evidence_supported"
            }
        ],
        "decisions": [
            {
                "title": "Enforce strict $5,000/month infrastructure cost ceiling for audio transcription pipeline",
                "description": "Any proposed architecture must satisfy the 72% cost reduction requirement.",
                "status": "confirmed",
                "source_evidence_quote": "Our budget cap for this quarter is strictly $5,000 per month. We need alternative architectural approaches immediately."
            }
        ],
        "risks": [
            {
                "title": "Client-side WASM thread limitations on legacy mobile browsers",
                "description": "Older Android mobile browsers may struggle with multithreaded WebAssembly silence elimination.",
                "severity": "medium",
                "potential_impact": "Audio stuttering or UI freezes on low-end mobile devices.",
                "suggested_mitigation": "Implement feature detection with graceful fallback to server-side processing for older devices.",
                "source_evidence_quote": "limitation is older Android browsers might struggle with WASM threads."
            }
        ],
        "creative_solutions": {
            "problem_statement": "Reduce audio transcription compute expenses from $18,000/mo to beneath the $5,000/mo quarterly budget cap.",
            "approaches": [
                {
                    "title": "Client-Side Browser WASM Pre-Filtering",
                    "explanation": "Offload voice activity detection (VAD) and silence clipping to the client browser before audio transmission over WebRTC.",
                    "expected_benefits": ["Eliminates 65% of transmitted audio stream data", "Zero server CPU spent on silent pauses"],
                    "limitations": ["Requires WebAssembly SIMD support on client device"],
                    "required_resources": ["VAD WASM package", "WebRTC track interceptor"],
                    "risks": ["Mobile browser battery drain"],
                    "assumptions": ["90% of meetings contain at least 40% non-speech pause time"],
                    "suggested_experiments": ["A/B test browser VAD accuracy across 50 sample recordings"],
                    "evaluation_criteria_scores": {"cost_reduction": 9.0, "implementation_effort": 6.5, "latency_impact": 8.5}
                },
                {
                    "title": "Qualcomm Cloud AI Hardware Accelerator Migration",
                    "explanation": "Deploy specialized Qualcomm Cloud AI inference nodes optimized for INT8/FP16 transformer matrix math.",
                    "expected_benefits": ["4x throughput per watt compared to generic cloud CPUs", "Sub-100ms transcription latency"],
                    "limitations": ["Requires initial quantization verification"],
                    "required_resources": ["Qualcomm Cloud AI instance", "Quantized model weights"],
                    "risks": ["Quantization accuracy drop if calibration dataset is too narrow"],
                    "assumptions": ["Models achieve <1% WER degradation under INT8 quantization"],
                    "suggested_experiments": ["Run Qualcomm AI inference benchmark against Librispeech test set"],
                    "evaluation_criteria_scores": {"cost_reduction": 8.5, "implementation_effort": 8.0, "latency_impact": 9.5}
                },
                {
                    "title": "Adaptive Audio Sample Rate Downsampling",
                    "explanation": "Dynamically switch audio from 48kHz to 16kHz mono when background noise is low.",
                    "expected_benefits": ["66% bandwidth reduction", "Lower memory footprint"],
                    "limitations": ["Slight loss of high frequency audio harmonics"],
                    "required_resources": ["Opus codec configuration update"],
                    "risks": ["Minor speech clarity reduction for accented speakers"],
                    "assumptions": ["16kHz is sufficient for ASR acoustic models"],
                    "suggested_experiments": ["Test ASR word error rate on 16kHz vs 48kHz inputs"],
                    "evaluation_criteria_scores": {"cost_reduction": 7.0, "implementation_effort": 9.0, "latency_impact": 8.0}
                }
            ]
        },
        "second_brain": {
            "what_we_believe": [
                {
                    "item": "Monthly audio processing expenses cannot exceed $5,000.",
                    "type": "constraint",
                    "evidence_quote": "Our budget cap for this quarter is strictly $5,000 per month."
                }
            ],
            "what_we_might_be_missing": [
                {
                    "finding": "Device fragmentation could cause silent failures in WASM VAD on older clients.",
                    "concern_type": "technical_risk",
                    "evidence_quote": "limitation is older Android browsers might struggle with WASM threads.",
                    "reasoning": "If client VAD crashes, audio is either lost or completely blocked.",
                    "potential_impact": "Missing meeting transcript segments for certain users.",
                    "confidence": "high",
                    "suggested_verification": "Test WebAssembly fallback on Chrome 85 and Android Webview."
                }
            ],
            "what_to_investigate_next": [
                {
                    "recommendation": "Quantify exact power and cost savings using Qualcomm Cloud AI hardware acceleration.",
                    "action_type": "research",
                    "suggested_owner": "Dev",
                    "rationale": "High throughput per watt directly translates to staying well under the $5,000 budget cap."
                }
            ]
        }
    }
}
