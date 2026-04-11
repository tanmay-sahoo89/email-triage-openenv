"""Workflow scenarios for the email_triage_workflow task.

Each scenario ties an email to the expected end-to-end triage actions:
classify → route → set SLA → (maybe escalate) → draft → close.
"""

from src.models import (
    Email,
    EmailCategory,
    EmailPriority,
    ImpactDomain,
    WorkflowScenario,
)


WORKFLOW_SCENARIOS: list[WorkflowScenario] = [
    # ── P0: security incident ──────────────────────────────────────────────
    WorkflowScenario(
        id="wf01",
        email=Email(
            id="wf01-email",
            sender="ciso@enterprise-client.com",
            subject="CRITICAL: Active data exfiltration detected from your API",
            body=(
                "Our SIEM just flagged what looks like active data exfiltration "
                "coming FROM your API service into an external IP (45.77.223.11). "
                "We see 420 MB transferred in the last 30 minutes. We have frozen "
                "our integration but need your security team on a call immediately. "
                "This may be a zero-day in your platform.\n\nCISO, Enterprise Client"
            ),
            timestamp="2025-04-03T02:14:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
        ),
        expected_route="security_team",
        expected_sla_hours=1,
        expected_escalation=True,
        expected_ticket_severity="P0",
        expected_reply_keywords=["security", "investigat", "call", "incident", "confirm", "isolate"],
    ),

    # ── P0: healthcare safety issue ────────────────────────────────────────
    WorkflowScenario(
        id="wf02",
        email=Email(
            id="wf02-email",
            sender="safety@childrenshospital.org",
            subject="URGENT: Infusion pump firmware bug - pediatric patients at risk",
            body=(
                "Dear Vendor,\n\nWe have documented 4 instances in 24 hours where "
                "your Model IP-220 infusion pump miscalculated the dose for "
                "pediatric patients (under 20 kg). A 3-year-old was given "
                "approximately 2x the prescribed acetaminophen dose. Patient is "
                "stable but this is a serious safety issue.\n\nWe've filed an "
                "FDA MDR. Need your Quality team on this TODAY.\n\n"
                "Dr. Chen, Patient Safety Officer\nChildren's Hospital"
            ),
            timestamp="2025-03-22T07:15:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.MEDICAL,
            impact_domain=ImpactDomain.HEALTHCARE,
        ),
        expected_route="exec_escalation",
        expected_sla_hours=2,
        expected_escalation=True,
        expected_ticket_severity="P0",
        expected_reply_keywords=["safety", "urgent", "quality", "investigat", "recall", "team"],
    ),

    # ── P1: paying customer down ──────────────────────────────────────────
    WorkflowScenario(
        id="wf03",
        email=Email(
            id="wf03-email",
            sender="ops@fintech-startup.io",
            subject="Production down - all payments failing 500 errors",
            body=(
                "Our entire production environment is returning 500s from your "
                "payment API since 14:02 UTC. We're losing ~$1200/minute in "
                "transactions. Enterprise plan, account ID ACC-2201. Please "
                "escalate to on-call engineering immediately.\n\nOps Team"
            ),
            timestamp="2025-04-01T14:10:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.TECHNICAL,
        ),
        expected_route="eng_oncall",
        expected_sla_hours=1,
        expected_escalation=True,
        expected_ticket_severity="P1",
        expected_reply_keywords=["engineer", "incident", "status", "investigat", "update"],
    ),

    # ── P2: standard billing dispute ───────────────────────────────────────
    WorkflowScenario(
        id="wf04",
        email=Email(
            id="wf04-email",
            sender="accounting@midsize-corp.com",
            subject="Invoice INV-2025-0319 - line items don't match our PO",
            body=(
                "Hi,\n\nInvoice INV-2025-0319 for $8,450 has two line items "
                "('Premium Support Add-on' and 'Training Session Pack') that "
                "were not on our purchase order PO-2025-114. Could you send a "
                "corrected invoice? We'll process once it matches the PO.\n\n"
                "No rush, just flag for billing team.\n\nAccounts Payable"
            ),
            timestamp="2025-03-29T10:00:00Z",
            priority=EmailPriority.NORMAL,
            category=EmailCategory.BILLING,
        ),
        expected_route="billing_team",
        expected_sla_hours=48,
        expected_escalation=False,
        expected_ticket_severity="P3",
        expected_reply_keywords=["invoice", "review", "correct", "billing", "team"],
    ),

    # ── P1: GDPR legal escalation ──────────────────────────────────────────
    WorkflowScenario(
        id="wf05",
        email=Email(
            id="wf05-email",
            sender="legal@eu-regulator.europa.eu",
            subject="GDPR Formal Complaint Ref EU-2025-1147 - 14 day response",
            body=(
                "Pursuant to Article 77 of Regulation (EU) 2016/679, a formal "
                "complaint has been filed against your organization by a data "
                "subject (ref: EU-2025-1147). You are required to provide a "
                "formal written response within 14 calendar days of receipt of "
                "this notice.\n\nFailure to respond may result in administrative "
                "fines up to 4% of global annual turnover.\n\n"
                "Data Protection Authority, EU"
            ),
            timestamp="2025-03-24T11:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.LEGAL,
            impact_domain=ImpactDomain.GDPR,
        ),
        expected_route="legal",
        expected_sla_hours=24,
        expected_escalation=True,
        expected_ticket_severity="P1",
        expected_reply_keywords=["legal", "acknowledge", "respond", "counsel", "14"],
    ),

    # ── P3: low-priority general inquiry ───────────────────────────────────
    WorkflowScenario(
        id="wf06",
        email=Email(
            id="wf06-email",
            sender="intern@smallstartup.co",
            subject="Question about integrating your API",
            body=(
                "Hi,\n\nI'm an intern exploring whether your API would work for "
                "a side project. Do you have a free tier? What's the rate limit? "
                "Also, which languages do your SDKs support?\n\nThanks!\nAlex"
            ),
            timestamp="2025-04-02T15:00:00Z",
            priority=EmailPriority.LOW,
            category=EmailCategory.GENERAL,
        ),
        expected_route="support_tier1",
        expected_sla_hours=72,
        expected_escalation=False,
        expected_ticket_severity="P3",
        expected_reply_keywords=["thank", "free", "docs", "rate", "help"],
    ),

    # ── P1: accessibility complaint with legal dimension ──────────────────
    WorkflowScenario(
        id="wf07",
        email=Email(
            id="wf07-email",
            sender="counsel@disability-rights.org",
            subject="ADA Title III complaint - formal notice before legal action",
            body=(
                "This is formal notice that we intend to file an ADA Title III "
                "lawsuit against your company within 30 days unless the following "
                "accessibility issues are resolved:\n\n"
                "1. Main dashboard fails WCAG 2.1 AA (color contrast 2.1:1)\n"
                "2. Screen reader navigation broken on settings page\n"
                "3. No keyboard-only navigation for the onboarding flow\n\n"
                "We represent 1,200+ clients who depend on assistive technologies. "
                "Please have your legal counsel respond within 10 business days.\n\n"
                "Disability Rights Advocacy"
            ),
            timestamp="2025-03-26T13:30:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.LEGAL,
            impact_domain=ImpactDomain.ACCESSIBILITY,
        ),
        expected_route="legal",
        expected_sla_hours=24,
        expected_escalation=True,
        expected_ticket_severity="P1",
        expected_reply_keywords=["legal", "accessibility", "wcag", "counsel", "acknowledge"],
    ),

    # ── P2: abuse report ───────────────────────────────────────────────────
    WorkflowScenario(
        id="wf08",
        email=Email(
            id="wf08-email",
            sender="safety@ngo-child-protection.org",
            subject="Report: user account distributing harmful content to minors",
            body=(
                "We have identified account @user_3342 on your platform distributing "
                "inappropriate content targeting minors. We've collected evidence "
                "(screenshots attached) and reported to NCMEC. Please act urgently "
                "to suspend the account and preserve evidence.\n\n"
                "Trust & Safety, NGO Child Protection"
            ),
            timestamp="2025-03-25T09:00:00Z",
            priority=EmailPriority.URGENT,
            category=EmailCategory.SECURITY,
            impact_domain=ImpactDomain.CHILD_SAFETY,
        ),
        expected_route="abuse_desk",
        expected_sla_hours=2,
        expected_escalation=True,
        expected_ticket_severity="P1",
        expected_reply_keywords=["safety", "suspend", "preserve", "investigat", "acknowledge"],
    ),
]
