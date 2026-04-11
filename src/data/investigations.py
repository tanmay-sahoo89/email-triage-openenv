"""Investigation scenarios for the email_investigate task.

Each scenario bundles:
  - An email (the thing to investigate)
  - A ground-truth verdict
  - A ``hidden_knowledge`` dict that tool handlers peek into to simulate
    external systems (threat intel DB, WHOIS, CRM, URL sandbox, etc.)
  - Critical evidence tools — the ones the agent really should call
  - Red flags — human-readable, for the grader to reward reasoning that
    mentions them in the final justification.

This dataset is the core of what turns the env into a **true interactive
investigation sandbox** instead of a graded quiz.
"""

from src.models import (
    Email,
    EmailCategory,
    EmailPriority,
    ImpactDomain,
    InvestigationScenario,
)


INVESTIGATION_SCENARIOS: list[InvestigationScenario] = [
    # ── 1. Classic BEC (Business Email Compromise) — CEO impersonation ──────
    InvestigationScenario(
        id="inv01",
        email=Email(
            id="inv01-email",
            sender="john.harrison@ceo-company.co",  # typosquat of ceo@company.com
            subject="Urgent wire transfer needed - confidential",
            body=(
                "Hi Sarah,\n\nI'm in a meeting with our acquisition target and I need "
                "you to process an urgent wire transfer of $485,000 to the attached "
                "account details. This is highly confidential — do NOT discuss with "
                "anyone, including finance team. I need confirmation within the hour.\n\n"
                "Wire to: Acme Holdings LLC, Account 8829301, Routing 021000021\n\n"
                "Sent from my iPhone\nJohn Harrison, CEO"
            ),
            timestamp="2025-03-12T14:23:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            is_phishing=True,
            impact_domain=ImpactDomain.FINANCIAL_CRIME,
            headers={"reply-to": "j.harrison.exec@protonmail.com"},
        ),
        ground_truth_verdict="bec",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_internal_directory",
            "check_spf_dkim_dmarc",
        ],
        red_flags=[
            "Domain typosquat: ceo-company.co vs real company.com",
            "Reply-to mismatch: protonmail personal address",
            "Urgency + secrecy + wire transfer = classic BEC pattern",
            "SPF/DKIM fail",
        ],
        hidden_knowledge={
            "domain_whois": {
                "ceo-company.co": {
                    "domain": "ceo-company.co",
                    "registered_days_ago": 4,
                    "registrar": "Namecheap",
                    "country": "RU",
                    "privacy_protected": True,
                    "malicious_list": True,
                }
            },
            "internal_directory": {
                "john harrison": {
                    "name": "John Harrison",
                    "found": True,
                    "title": "CEO",
                    "real_email": "john.harrison@company.com",
                    "match_confidence": 0.95,
                }
            },
            "email_auth": {"spf": "fail", "dkim": "fail", "dmarc": "fail", "alignment": False},
            "sender_reputation": {
                "john.harrison@ceo-company.co": {
                    "email": "john.harrison@ceo-company.co",
                    "reputation": "malicious",
                    "score": 12,
                    "known_abuser": True,
                    "incident_count": 14,
                    "first_seen_days_ago": 4,
                }
            },
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.FINANCIAL_CRIME,
    ),

    # ── 2. Legitimate invoice from a real vendor ────────────────────────────
    InvestigationScenario(
        id="inv02",
        email=Email(
            id="inv02-email",
            sender="billing@stripe.com",
            subject="Your Stripe invoice for March 2025 is available",
            body=(
                "Hi there,\n\nYour monthly Stripe invoice for March 2025 is now "
                "available in your dashboard. Amount: $2,349.17 (processing fees). "
                "This will be auto-deducted on April 5th.\n\n"
                "View invoice: https://dashboard.stripe.com/invoices/in_1PQ8\n\n"
                "Questions? Reply to this email or contact support.\n\n"
                "— Stripe Billing"
            ),
            timestamp="2025-04-01T09:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.BILLING,
            is_phishing=False,
        ),
        ground_truth_verdict="legitimate",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_spf_dkim_dmarc",
            "query_customer_record",
        ],
        red_flags=[],
        hidden_knowledge={
            "domain_whois": {
                "stripe.com": {
                    "domain": "stripe.com",
                    "registered_days_ago": 6720,
                    "registrar": "MarkMonitor",
                    "country": "US",
                    "privacy_protected": False,
                    "malicious_list": False,
                }
            },
            "email_auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
            "sender_reputation": {
                "billing@stripe.com": {
                    "email": "billing@stripe.com",
                    "reputation": "trusted",
                    "score": 98,
                    "known_abuser": False,
                    "incident_count": 0,
                    "first_seen_days_ago": 3500,
                }
            },
            "customer_records": {
                "billing@stripe.com": {
                    "email": "billing@stripe.com",
                    "account_exists": True,
                    "tier": "vendor",
                    "open_tickets": 0,
                    "payment_status": "current",
                    "verified_identity": True,
                }
            },
            "url_verdicts": {"https://dashboard.stripe.com/invoices/in_1pq8": "safe"},
        },
        minimum_tools_required=1,
    ),

    # ── 3. Crypto scam targeting a child safety organization ────────────────
    InvestigationScenario(
        id="inv03",
        email=Email(
            id="inv03-email",
            sender="director@unicef-donations-global.org",
            subject="Emergency donation request - help Ukrainian children",
            body=(
                "Dear Friend of the Children,\n\nUNICEF is coordinating emergency "
                "aid for displaced Ukrainian children. Due to banking restrictions, "
                "we can only accept donations via cryptocurrency at this time.\n\n"
                "Please send ETH to: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1\n\n"
                "Every $50 feeds a child for one week. Please share this with your "
                "network. 100% of donations go directly to aid.\n\n"
                "Director of Emergency Response\nUNICEF Global"
            ),
            timestamp="2025-02-18T10:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            is_phishing=True,
            impact_domain=ImpactDomain.HUMANITARIAN,
        ),
        ground_truth_verdict="scam",
        critical_evidence_tools=[
            "check_domain_registration",
            "scan_body_for_iocs",
            "search_past_incidents",
        ],
        red_flags=[
            "Crypto-only donation (real charities don't do this)",
            "Domain unicef-donations-global.org is NOT real UNICEF (unicef.org)",
            "Urgency + emotional appeal + irreversible payment method",
        ],
        hidden_knowledge={
            "domain_whois": {
                "unicef-donations-global.org": {
                    "domain": "unicef-donations-global.org",
                    "registered_days_ago": 11,
                    "registrar": "Porkbun",
                    "country": "NG",
                    "privacy_protected": True,
                    "malicious_list": True,
                }
            },
            "past_incidents": [
                {
                    "id": "inc-2024-0892",
                    "summary": "Fake UNICEF crypto donation scam targeting NGOs",
                    "severity": "high",
                },
                {
                    "id": "inc-2025-0114",
                    "summary": "ETH wallet 0x742d35... linked to 12 prior Ukraine donation scams",
                    "severity": "high",
                },
            ],
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.HUMANITARIAN,
    ),

    # ── 4. Legitimate urgent healthcare emergency ───────────────────────────
    InvestigationScenario(
        id="inv04",
        email=Email(
            id="inv04-email",
            sender="dr.patel@memorialhospital.org",
            subject="URGENT: Ventilator firmware bug affecting ICU patients",
            body=(
                "To whom it may concern,\n\nWe've identified a firmware bug in your "
                "V-4200 ventilator model that causes spurious alarms and occasional "
                "pressure drops. Six of our ICU patients have been affected in the "
                "past 48 hours. No fatalities yet but we need an urgent fix or "
                "recall guidance.\n\nI am Dr. Raj Patel, ICU Medical Director at "
                "Memorial Hospital. I've already contacted FDA MedWatch (case "
                "#MW-2025-3397). Please contact me directly at +1-555-204-8812.\n\n"
                "This is a patient safety issue.\n\nDr. Raj Patel, MD"
            ),
            timestamp="2025-03-20T03:14:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.MEDICAL,
            is_phishing=False,
            impact_domain=ImpactDomain.HEALTHCARE,
        ),
        ground_truth_verdict="legitimate",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_spf_dkim_dmarc",
            "lookup_sender_reputation",
        ],
        red_flags=[],
        hidden_knowledge={
            "domain_whois": {
                "memorialhospital.org": {
                    "domain": "memorialhospital.org",
                    "registered_days_ago": 4821,
                    "registrar": "Network Solutions",
                    "country": "US",
                    "privacy_protected": False,
                    "malicious_list": False,
                }
            },
            "email_auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
            "sender_reputation": {
                "dr.patel@memorialhospital.org": {
                    "email": "dr.patel@memorialhospital.org",
                    "reputation": "trusted",
                    "score": 88,
                    "known_abuser": False,
                    "incident_count": 0,
                    "first_seen_days_ago": 1204,
                }
            },
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.HEALTHCARE,
    ),

    # ── 5. Subtle credential phishing ───────────────────────────────────────
    InvestigationScenario(
        id="inv05",
        email=Email(
            id="inv05-email",
            sender="no-reply@microsof1-security.com",
            subject="Unusual sign-in activity on your Microsoft account",
            body=(
                "We detected an unusual sign-in attempt on your Microsoft account "
                "from Moscow, Russia at 14:22 UTC.\n\nIf this was not you, please "
                "verify your identity to secure your account:\n\n"
                "https://microsof1-security.com/verify?id=7829\n\n"
                "If you don't respond within 24 hours, your account will be "
                "temporarily suspended.\n\nMicrosoft Account Team"
            ),
            timestamp="2025-03-25T18:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            is_phishing=True,
        ),
        ground_truth_verdict="phishing",
        critical_evidence_tools=[
            "check_domain_registration",
            "verify_link_safety",
            "check_spf_dkim_dmarc",
        ],
        red_flags=[
            "Typosquat domain: microsof1-security.com (note the '1' replacing 't')",
            "Urgency + credential request",
            "Link goes to non-Microsoft domain",
        ],
        hidden_knowledge={
            "domain_whois": {
                "microsof1-security.com": {
                    "domain": "microsof1-security.com",
                    "registered_days_ago": 2,
                    "registrar": "NameSilo",
                    "country": "RU",
                    "privacy_protected": True,
                    "malicious_list": True,
                }
            },
            "url_verdicts": {
                "https://microsof1-security.com/verify?id=7829": "malicious",
                "https://microsof1-security.com/verify?id=7829:redirect": "https://credential-harvest.biz/login",
            },
            "email_auth": {"spf": "fail", "dkim": "fail", "dmarc": "fail", "alignment": False},
        },
        minimum_tools_required=2,
    ),

    # ── 6. Legitimate humanitarian coordination (disaster response) ────────
    InvestigationScenario(
        id="inv06",
        email=Email(
            id="inv06-email",
            sender="coordinator@unocha.org",
            subject="Request for satellite imagery - Myanmar earthquake response",
            body=(
                "Hello,\n\nOCHA is coordinating the humanitarian response to the "
                "March 28 Myanmar earthquake (M7.7). We need access to your recent "
                "satellite imagery of the Sagaing and Mandalay regions to identify "
                "damaged villages that have not yet been reached by ground teams.\n\n"
                "Under the International Charter Space and Major Disasters, this "
                "data should be made available free of charge for humanitarian use. "
                "Please provide access to imagery from March 28-April 3.\n\n"
                "Activation ID: CHARTER-2025-0328-MYA\n\n"
                "Regards,\nMaria Kovacs\nEmergency Coordinator, UN OCHA"
            ),
            timestamp="2025-04-01T08:30:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.HUMANITARIAN,
            is_phishing=False,
            impact_domain=ImpactDomain.DISASTER_RESPONSE,
        ),
        ground_truth_verdict="legitimate",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_spf_dkim_dmarc",
            "search_past_incidents",
        ],
        red_flags=[],
        hidden_knowledge={
            "domain_whois": {
                "unocha.org": {
                    "domain": "unocha.org",
                    "registered_days_ago": 9125,
                    "registrar": "UN ICT",
                    "country": "CH",
                    "privacy_protected": False,
                    "malicious_list": False,
                }
            },
            "email_auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
            "past_incidents": [
                {
                    "id": "charter-2024-0901",
                    "summary": "Prior OCHA charter request for Libya floods - legitimate and fulfilled",
                    "severity": "info",
                }
            ],
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.DISASTER_RESPONSE,
    ),

    # ── 7. Multilingual phishing (Spanish → sketchy link) ───────────────────
    InvestigationScenario(
        id="inv07",
        email=Email(
            id="inv07-email",
            sender="seguridad@bancosantander-verify.es",
            subject="Alerta de seguridad: acceso no autorizado detectado",
            body=(
                "Estimado cliente,\n\nHemos detectado un acceso no autorizado a "
                "su cuenta desde una ubicación desconocida. Por favor verifique "
                "su identidad en el siguiente enlace dentro de 24 horas o su "
                "cuenta será bloqueada:\n\n"
                "https://bancosantander-verify.es/confirmar\n\n"
                "Gracias,\nEquipo de Seguridad Banco Santander"
            ),
            timestamp="2025-03-10T16:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            is_phishing=True,
            language="es",
        ),
        ground_truth_verdict="phishing",
        critical_evidence_tools=[
            "translate_body",
            "check_domain_registration",
            "verify_link_safety",
        ],
        red_flags=[
            "Domain bancosantander-verify.es is not the real santander.com / bancosantander.es",
            "Urgency + credential request pattern",
        ],
        hidden_knowledge={
            "translation": (
                "Dear customer, we have detected unauthorized access to your "
                "account from an unknown location. Please verify your identity "
                "at the following link within 24 hours or your account will be "
                "blocked: https://bancosantander-verify.es/confirmar"
            ),
            "domain_whois": {
                "bancosantander-verify.es": {
                    "domain": "bancosantander-verify.es",
                    "registered_days_ago": 9,
                    "registrar": "OVH",
                    "country": "FR",
                    "privacy_protected": True,
                    "malicious_list": True,
                }
            },
            "url_verdicts": {
                "https://bancosantander-verify.es/confirmar": "malicious",
            },
            "email_auth": {"spf": "fail", "dkim": "fail", "dmarc": "fail", "alignment": False},
        },
        minimum_tools_required=2,
    ),

    # ── 8. Ransomware extortion ─────────────────────────────────────────────
    InvestigationScenario(
        id="inv08",
        email=Email(
            id="inv08-email",
            sender="recovery@dark-help.onion-mail.com",
            subject="Your data has been encrypted - read immediately",
            body=(
                "Your company's servers have been encrypted by BlackCat ransomware. "
                "We have also exfiltrated 2.3 TB of sensitive customer data including "
                "healthcare records and payment information.\n\nTo receive the "
                "decryption key and prevent publication of stolen data, send 45 "
                "BTC to: bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n\n"
                "You have 72 hours. After that, the ransom doubles and data will "
                "be published on our leak site.\n\nProof of attack: attached file list.\n\nBlackCat Team"
            ),
            timestamp="2025-03-30T02:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            is_phishing=True,
            impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
        ),
        ground_truth_verdict="scam",
        critical_evidence_tools=[
            "scan_body_for_iocs",
            "search_past_incidents",
            "check_domain_registration",
        ],
        red_flags=[
            "BTC ransom demand",
            "BlackCat ransomware branding",
            "Onion-mail sender domain",
            "Extortion + time pressure",
        ],
        hidden_knowledge={
            "domain_whois": {
                "onion-mail.com": {
                    "domain": "onion-mail.com",
                    "registered_days_ago": 890,
                    "registrar": "Njalla",
                    "country": "SE",
                    "privacy_protected": True,
                    "malicious_list": True,
                }
            },
            "past_incidents": [
                {
                    "id": "ransom-2025-0221",
                    "summary": "BlackCat ransomware BTC wallet bc1qar0srrr... linked to 47 prior extortion attempts",
                    "severity": "critical",
                }
            ],
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
    ),

    # ── 9. Suspicious but ultimately legitimate password-reset ─────────────
    InvestigationScenario(
        id="inv09",
        email=Email(
            id="inv09-email",
            sender="no-reply@accounts.google.com",
            subject="Security alert: new sign-in from Chrome on Windows",
            body=(
                "A new sign-in on Windows\n\nYour Google Account was just signed "
                "in to from a new Windows device. You're getting this email to "
                "make sure it was you.\n\nCheck activity: https://myaccount.google.com/notifications\n\n"
                "If you don't recognize this activity, secure your account."
            ),
            timestamp="2025-04-02T13:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.SECURITY,
            is_phishing=False,
        ),
        ground_truth_verdict="legitimate",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_spf_dkim_dmarc",
            "verify_link_safety",
        ],
        red_flags=[],
        hidden_knowledge={
            "domain_whois": {
                "google.com": {
                    "domain": "google.com",
                    "registered_days_ago": 10950,
                    "registrar": "MarkMonitor",
                    "country": "US",
                    "privacy_protected": False,
                    "malicious_list": False,
                }
            },
            "email_auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
            "url_verdicts": {
                "https://myaccount.google.com/notifications": "safe",
            },
        },
        minimum_tools_required=1,
    ),

    # ── 10. Supply chain fraud targeting critical infrastructure ────────────
    InvestigationScenario(
        id="inv10",
        email=Email(
            id="inv10-email",
            sender="procurement@siemens-energy-global.net",
            subject="Updated banking details for outstanding invoice EG-2025-0412",
            body=(
                "Dear Accounts Payable,\n\nDue to a recent banking consolidation, "
                "Siemens Energy has updated its remittance details. Please use the "
                "following account for all future payments, including outstanding "
                "invoice EG-2025-0412 ($1,247,500):\n\n"
                "Bank: FirstCaribbean International Bank\nAccount: 8829-4471-0239\n"
                "SWIFT: FCIBBSNS\nBeneficiary: Siemens Energy Procurement Ltd\n\n"
                "Please confirm receipt and update your vendor master file.\n\n"
                "Regards,\nAccounts Receivable, Siemens Energy"
            ),
            timestamp="2025-03-28T11:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.BILLING,
            is_phishing=True,
            impact_domain=ImpactDomain.SUPPLY_CHAIN,
        ),
        ground_truth_verdict="bec",
        critical_evidence_tools=[
            "check_domain_registration",
            "query_customer_record",
            "search_past_incidents",
        ],
        red_flags=[
            "Domain siemens-energy-global.net is NOT the real siemens-energy.com",
            "Banking-details-change request = classic invoice fraud",
            "Caribbean offshore bank for a European vendor",
        ],
        hidden_knowledge={
            "domain_whois": {
                "siemens-energy-global.net": {
                    "domain": "siemens-energy-global.net",
                    "registered_days_ago": 16,
                    "registrar": "Dynadot",
                    "country": "PH",
                    "privacy_protected": True,
                    "malicious_list": False,
                }
            },
            "customer_records": {
                "procurement@siemens-energy-global.net": {
                    "email": "procurement@siemens-energy-global.net",
                    "account_exists": False,
                    "tier": None,
                    "open_tickets": 0,
                    "payment_status": "n/a",
                    "verified_identity": False,
                },
                "accounts@siemens-energy.com": {
                    "email": "accounts@siemens-energy.com",
                    "account_exists": True,
                    "tier": "enterprise_vendor",
                    "open_tickets": 0,
                    "payment_status": "current",
                    "verified_identity": True,
                    "verified_bank": "Deutsche Bank DE89370400440532013000",
                },
            },
            "past_incidents": [
                {
                    "id": "bec-2024-1107",
                    "summary": "Siemens-Energy vendor impersonation with banking details change - $3.2M loss",
                    "severity": "critical",
                }
            ],
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.SUPPLY_CHAIN,
    ),

    # ── 11. Social engineering targeting accessibility org ─────────────────
    InvestigationScenario(
        id="inv11",
        email=Email(
            id="inv11-email",
            sender="support@assistive-tech-donors.info",
            subject="Your application for assistive tech grant is approved!",
            body=(
                "Congratulations!\n\nYour application for a $15,000 assistive "
                "technology grant has been APPROVED by the Global Accessibility "
                "Foundation.\n\nTo receive your funds, please provide:\n"
                "1. Full legal name\n2. Bank account and routing numbers\n"
                "3. Social Security Number\n4. A $199 processing fee (refundable)\n\n"
                "Reply within 5 business days to claim your grant.\n\n"
                "Global Accessibility Foundation"
            ),
            timestamp="2025-03-15T10:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.SECURITY,
            is_phishing=True,
            impact_domain=ImpactDomain.ACCESSIBILITY,
        ),
        ground_truth_verdict="scam",
        critical_evidence_tools=[
            "check_domain_registration",
            "lookup_sender_reputation",
            "search_past_incidents",
        ],
        red_flags=[
            "Upfront 'processing fee' is a classic advance-fee scam",
            "Requesting SSN + bank details",
            "Unsolicited grant award",
        ],
        hidden_knowledge={
            "domain_whois": {
                "assistive-tech-donors.info": {
                    "domain": "assistive-tech-donors.info",
                    "registered_days_ago": 22,
                    "registrar": "Porkbun",
                    "country": "US",
                    "privacy_protected": True,
                    "malicious_list": False,
                }
            },
            "sender_reputation": {
                "support@assistive-tech-donors.info": {
                    "email": "support@assistive-tech-donors.info",
                    "reputation": "suspicious",
                    "score": 22,
                    "known_abuser": True,
                    "incident_count": 6,
                    "first_seen_days_ago": 22,
                }
            },
            "past_incidents": [
                {
                    "id": "advfee-2025-0088",
                    "summary": "Advance-fee grant scam targeting disability organizations",
                    "severity": "high",
                }
            ],
        },
        minimum_tools_required=2,
        impact_domain=ImpactDomain.ACCESSIBILITY,
    ),

    # ── 12. Legitimate GDPR data request ───────────────────────────────────
    InvestigationScenario(
        id="inv12",
        email=Email(
            id="inv12-email",
            sender="dpo@telefonica.com",
            subject="GDPR Article 15 Data Access Request - Ref DPO-2025-8821",
            body=(
                "Hello,\n\nUnder Article 15 of the EU General Data Protection "
                "Regulation, I am formally requesting a copy of all personal data "
                "you hold on our joint customer account (contract #TEF-443-99201).\n\n"
                "Per GDPR, you must respond within 30 days. Please provide the data "
                "in a machine-readable format (JSON or CSV).\n\n"
                "This request is submitted under my role as Data Protection Officer "
                "for Telefónica España. Please reply to this address for confirmation.\n\n"
                "Regards,\nDPO Office, Telefónica"
            ),
            timestamp="2025-03-18T09:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.LEGAL,
            is_phishing=False,
            impact_domain=ImpactDomain.GDPR,
        ),
        ground_truth_verdict="legitimate",
        critical_evidence_tools=[
            "check_domain_registration",
            "check_spf_dkim_dmarc",
        ],
        red_flags=[],
        hidden_knowledge={
            "domain_whois": {
                "telefonica.com": {
                    "domain": "telefonica.com",
                    "registered_days_ago": 10500,
                    "registrar": "MarkMonitor",
                    "country": "ES",
                    "privacy_protected": False,
                    "malicious_list": False,
                }
            },
            "email_auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "alignment": True},
        },
        minimum_tools_required=1,
        impact_domain=ImpactDomain.GDPR,
    ),
]
