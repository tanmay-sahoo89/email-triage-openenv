"""Synthetic email datasets for all tasks.

Global-impact scenarios span healthcare, disaster response, financial crime,
humanitarian coordination, accessibility, GDPR, child safety, critical
infrastructure, and supply chain — carefully curated so training on this
environment produces email agents that handle **real-world high-stakes**
triage, not just generic customer-support tickets.
"""

from src.models import Email, EmailPriority, EmailCategory, EmailThread, ImpactDomain

# ─── TASK 1: Classification Emails (12 emails) ──────────────────────────────

CLASSIFY_EMAILS: list[Email] = [
    Email(
        id="c01",
        sender="john.smith@acmecorp.com",
        subject="URGENT: Payment declined - service at risk",
        body=(
            "Hi Support,\n\nOur monthly subscription payment of $2,499.99 was declined "
            "this morning. Our entire engineering team (45 people) relies on this service "
            "daily. If not resolved within 24 hours, we'll lose access to all our projects.\n\n"
            "Card on file ends in 4821. Please advise immediately.\n\nJohn Smith\nVP Engineering, Acme Corp"
        ),
        timestamp="2024-01-15T09:23:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.BILLING,
    ),
    Email(
        id="c02",
        sender="sarah.jones@techstart.io",
        subject="Cannot deploy to production - build failing",
        body=(
            "Our CI/CD pipeline has been failing for the past 2 hours with error: "
            "'Module not found: @internal/auth-provider'. This started after the v3.2.1 "
            "update was pushed. We have a client demo in 3 hours and cannot ship the fix.\n\n"
            "Build logs attached. Environment: Node 18, Ubuntu 22.04.\n\nSarah Jones\nCTO, TechStart"
        ),
        timestamp="2024-01-15T10:05:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.TECHNICAL,
    ),
    Email(
        id="c03",
        sender="mike.chen@globalretail.com",
        subject="Question about enterprise pricing tiers",
        body=(
            "Hello,\n\nWe're evaluating your platform for our retail chain (200+ stores). "
            "Could you send over the enterprise pricing sheet? We're particularly interested "
            "in the multi-tenant setup and SSO integration options.\n\nNo rush on this — we're "
            "in the early evaluation phase. Meeting with stakeholders next month.\n\nBest,\nMike Chen"
        ),
        timestamp="2024-01-15T11:30:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.GENERAL,
    ),
    Email(
        id="c04",
        sender="lisa.wang@mediahub.net",
        subject="Charged twice for January subscription",
        body=(
            "I just checked my credit card statement and I see TWO charges of $79.99 from "
            "your company on January 3rd. Transaction IDs: TXN-88291 and TXN-88294. I only "
            "have one account (lisa.wang@mediahub.net).\n\nPlease refund the duplicate charge. "
            "This is the second time this has happened.\n\nLisa Wang"
        ),
        timestamp="2024-01-15T12:15:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.BILLING,
    ),
    Email(
        id="c05",
        sender="dev.team@startup.co",
        subject="API rate limiting not working as documented",
        body=(
            "We're hitting 429 errors after only 50 requests/minute, but our plan allows "
            "500 req/min according to the docs. This has been happening consistently since "
            "Monday. We've verified our API key is correct and our plan is active.\n\n"
            "Can you check if there's an issue with the rate limiter on your end?\n\nDev Team, Startup.co"
        ),
        timestamp="2024-01-15T13:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.TECHNICAL,
    ),
    Email(
        id="c06",
        sender="hr@bigcompany.com",
        subject="Newsletter preferences update",
        body=(
            "Hi there,\n\nCould you update our email preferences? We'd like to receive the "
            "monthly product newsletter but opt out of the weekly tips emails. Our account "
            "email is hr@bigcompany.com.\n\nThanks!\nHR Department"
        ),
        timestamp="2024-01-15T14:20:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.GENERAL,
    ),
    Email(
        id="c07",
        sender="angry.user@email.com",
        subject="Your product ruined my presentation!!!",
        body=(
            "I was giving a LIVE DEMO to our board of directors and your app crashed "
            "right in the middle of it! The loading spinner just kept going for 10 minutes. "
            "I looked like a complete fool in front of the CEO. This is UNACCEPTABLE. "
            "I want a full refund and I'm cancelling immediately. WORST. SERVICE. EVER."
        ),
        timestamp="2024-01-15T15:45:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="c08",
        sender="security-alert@your-bank-verify.com",
        subject="URGENT: Your account has been compromised - verify now",
        body=(
            "Dear valued customer,\n\nWe have detected suspicious activity on your account. "
            "Your account will be LOCKED within 24 hours unless you verify your identity.\n\n"
            "Click here to verify: http://totally-legit-bank.com/verify\n\n"
            "Please provide your full name, SSN, and credit card number to restore access.\n\n"
            "Bank Security Team"
        ),
        timestamp="2024-01-15T16:00:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.SECURITY,
        is_phishing=True,
    ),
    Email(
        id="c09",
        sender="ops@datacenter.io",
        subject="CRITICAL: Database cluster failover in progress",
        body=(
            "ALERT: Primary database node db-primary-us-east-1 is unresponsive. "
            "Automatic failover to db-replica-us-east-2 initiated at 16:32 UTC. "
            "Estimated recovery time: 15-30 minutes. All write operations are queued. "
            "Read operations may experience 2-5s latency.\n\nIncident ID: INC-2024-0115-001"
        ),
        timestamp="2024-01-15T16:32:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.TECHNICAL,
    ),
    Email(
        id="c10",
        sender="feedback@happycustomer.org",
        subject="Great experience with your support team",
        body=(
            "Just wanted to say thanks to your support agent Maria who helped me set up "
            "the webhook integration yesterday. She was patient, knowledgeable, and even "
            "followed up this morning to make sure everything was working. You have a great "
            "team! Keep up the good work.\n\nBest regards"
        ),
        timestamp="2024-01-15T17:00:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.GENERAL,
    ),
    Email(
        id="c11",
        sender="finance@partner.com",
        subject="Invoice #INV-2024-0089 payment confirmation needed",
        body=(
            "Hello,\n\nWe processed payment for invoice #INV-2024-0089 ($12,500) via wire "
            "transfer on January 12th. Could you confirm receipt and update our account status? "
            "Our net-30 terms require confirmation within 5 business days.\n\nRegards,\nFinance Dept"
        ),
        timestamp="2024-01-16T08:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.BILLING,
    ),
    Email(
        id="c12",
        sender="admin@suspicious-domain.xyz",
        subject="You've won a $10,000 gift card!",
        body=(
            "Congratulations! You have been selected as the winner of our monthly draw. "
            "To claim your $10,000 Amazon gift card, simply reply with your full name, "
            "address, and bank account details for direct deposit.\n\n"
            "This offer expires in 48 hours. Act now!\n\nRewards Team"
        ),
        timestamp="2024-01-16T09:15:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.SECURITY,
        is_phishing=True,
    ),
]


# ─── TASK 2: Complaint Emails for Response Drafting (10 emails) ──────────────

RESPOND_EMAILS: list[Email] = [
    Email(
        id="r01",
        sender="frustrated.customer@gmail.com",
        subject="3 weeks and still no refund!",
        body=(
            "I requested a refund on December 28th (ticket #RF-4421) and was told it would "
            "take 5-7 business days. It's now January 18th — that's THREE WEEKS — and I "
            "still haven't received my $199.99 back. I've called twice and each time I'm "
            "told 'it's being processed.' This is ridiculous. I want my money back NOW or "
            "I'm filing a chargeback with my bank."
        ),
        timestamp="2024-01-18T09:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="r02",
        sender="business.owner@shopify-store.com",
        subject="Integration broke my entire storefront",
        body=(
            "After installing your Shopify integration yesterday, my entire product catalog "
            "is showing wrong prices. Every single item is priced at $0.00. I've lost at "
            "least $3,000 in sales today because customers can't check out properly. I need "
            "this fixed IMMEDIATELY or I need you to remove the integration and restore my "
            "catalog from backup."
        ),
        timestamp="2024-01-18T10:30:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="r03",
        sender="longtime.user@company.com",
        subject="Disappointed with the new UI update",
        body=(
            "I've been a loyal customer for 4 years, and the recent UI redesign has made "
            "the product nearly unusable for my workflow. The dashboard I relied on daily is "
            "now buried under 3 menus. The keyboard shortcuts I memorized no longer work. "
            "I understand you want to modernize, but this feels like change for the sake of "
            "change. Please consider adding a 'classic mode' option."
        ),
        timestamp="2024-01-18T11:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
    ),
    Email(
        id="r04",
        sender="parent@family.net",
        subject="Inappropriate content shown to my child",
        body=(
            "My 10-year-old was using your kids' learning platform when an advertisement "
            "for a horror movie appeared on screen. This is supposed to be a CHILDREN'S "
            "app! I'm horrified and considering reporting this to the children's privacy "
            "commission. What are you going to do about this?"
        ),
        timestamp="2024-01-18T12:15:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="r05",
        sender="enterprise.admin@megacorp.com",
        subject="SLA violation - 4 hours of downtime",
        body=(
            "Our enterprise contract guarantees 99.95% uptime (SLA-ENT-2023-445). Yesterday, "
            "your service was down from 2:00 PM to 6:00 PM EST — that's 4 hours of complete "
            "outage affecting 2,000 users at our company. Per our contract, we're entitled to "
            "service credits. Please calculate the credit amount and apply it to our next invoice."
        ),
        timestamp="2024-01-18T13:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
    ),
    Email(
        id="r06",
        sender="new.user@trial.com",
        subject="Misleading free trial - charged without warning",
        body=(
            "I signed up for what was advertised as a 'free 14-day trial' on January 5th. "
            "Today I see a $49.99 charge on my card and it's only January 12th — that's only "
            "7 days! There was no warning email, no reminder before charging. This feels like "
            "a dark pattern. I want a refund and I want to cancel."
        ),
        timestamp="2024-01-18T14:30:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
    ),
    Email(
        id="r07",
        sender="accessibility@nonprofit.org",
        subject="Your product fails WCAG accessibility standards",
        body=(
            "We're a nonprofit serving visually impaired individuals. Your platform fails "
            "basic WCAG 2.1 AA standards: no alt text on images, poor color contrast ratios "
            "(2.1:1 instead of required 4.5:1), and screen readers can't navigate the main "
            "menu. Our members cannot use your service. When will these issues be addressed?"
        ),
        timestamp="2024-01-18T15:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
    ),
    Email(
        id="r08",
        sender="data.officer@eucompany.de",
        subject="GDPR data deletion request not fulfilled",
        body=(
            "On December 1st, I submitted a formal GDPR Article 17 'Right to Erasure' request "
            "(ref: GDPR-DEL-2023-892). The 30-day compliance window has passed and I can confirm "
            "my data is still present in your system — I can still log in and see my profile. "
            "This is a legal violation. Please confirm complete data deletion within 48 hours or "
            "we will escalate to our Data Protection Authority."
        ),
        timestamp="2024-01-18T16:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
    ),
    Email(
        id="r09",
        sender="small.biz@email.com",
        subject="Support agent was rude and unhelpful",
        body=(
            "I called your support line today about a billing issue. The agent (ID: AGT-2291) "
            "was dismissive, interrupted me multiple times, and eventually said 'that's not my "
            "problem' before transferring me to a dead line. I've been a paying customer for "
            "2 years. This is not the level of service I expect. I want to speak with a manager."
        ),
        timestamp="2024-01-18T17:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="r10",
        sender="developer@indie.dev",
        subject="API breaking changes with no migration path",
        body=(
            "You pushed breaking changes to the v2 API without any deprecation notice. The "
            "endpoint POST /api/v2/users now requires a completely different payload structure. "
            "My app has 10,000 users and it broke overnight. The migration guide links to a 404 "
            "page. I need either a rollback of the breaking changes or an actual working migration "
            "guide within 24 hours."
        ),
        timestamp="2024-01-18T18:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
    ),
]


# ─── TASK 3: Multi-Email Threads with Contradictions (5 threads) ─────────────

THREAD_SCENARIOS: list[EmailThread] = [
    EmailThread(
        id="th01",
        subject="Server migration timeline",
        emails=[
            Email(
                id="th01-e1",
                sender="cto@company.com",
                subject="Server migration timeline",
                body=(
                    "Team, we're migrating to AWS. Timeline: complete by end of February. "
                    "This is NOT urgent — we have plenty of time. Budget approved: $50,000. "
                    "Current servers are stable and under contract until March 31st."
                ),
                timestamp="2024-01-10T09:00:00Z",
                priority=EmailPriority.LOW,
                category=EmailCategory.TECHNICAL,
            ),
            Email(
                id="th01-e2",
                sender="sysadmin@company.com",
                subject="Re: Server migration timeline",
                body=(
                    "Update: our current hosting provider just notified us they're shutting "
                    "down our data center on February 5th — NOT March 31st as we thought. "
                    "We need to migrate everything within 3 weeks. This is now CRITICAL."
                ),
                timestamp="2024-01-12T14:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.TECHNICAL,
            ),
            Email(
                id="th01-e3",
                sender="cfo@company.com",
                subject="Re: Server migration timeline",
                body=(
                    "I spoke with the hosting provider. They confirmed the March 31st date "
                    "is correct — the February 5th notice was sent in error. We can keep our "
                    "original timeline. Budget remains at $50,000. No rush."
                ),
                timestamp="2024-01-13T10:00:00Z",
                priority=EmailPriority.LOW,
                category=EmailCategory.TECHNICAL,
            ),
            Email(
                id="th01-e4",
                sender="sysadmin@company.com",
                subject="Re: Server migration timeline",
                body=(
                    "I just got OFF the phone with the data center manager. The February 5th "
                    "date is REAL. The CFO spoke with sales, not operations. The physical "
                    "shutdown is happening regardless. I have the written confirmation. "
                    "We MUST escalate this NOW."
                ),
                timestamp="2024-01-13T15:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.TECHNICAL,
            ),
        ],
        contradictions=[
            "The CFO says March 31st is the correct shutdown date and February 5th was an error, "
            "but the sysadmin has written confirmation from the data center operations manager "
            "that February 5th is the real physical shutdown date."
        ],
        true_priority=EmailPriority.URGENT,
        expected_action_items=[
            "Verify shutdown date directly with data center operations (not sales)",
            "Begin emergency migration planning for February 5th deadline",
            "Escalate to CTO for resource reallocation",
            "Request budget increase if expedited migration costs exceed $50,000",
        ],
        expected_followup="Schedule an emergency meeting with all stakeholders within 24 hours to align on the true timeline.",
    ),
    EmailThread(
        id="th02",
        subject="Customer data breach response",
        emails=[
            Email(
                id="th02-e1",
                sender="security@company.com",
                subject="INCIDENT: Potential data breach detected",
                body=(
                    "At 03:42 UTC, our IDS flagged unusual data exfiltration from the customer "
                    "database. Approximately 15,000 records may be affected. We've isolated the "
                    "affected server and are investigating. NO customer payment data was exposed — "
                    "only email addresses and names."
                ),
                timestamp="2024-01-20T03:45:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
            ),
            Email(
                id="th02-e2",
                sender="dba@company.com",
                subject="Re: INCIDENT: Potential data breach detected",
                body=(
                    "I've completed my analysis. The breach is worse than initially reported. "
                    "It's not 15,000 records — it's 150,000. And payment card tokens WERE in "
                    "the affected tables. We need to notify the payment processor immediately "
                    "and begin PCI incident response."
                ),
                timestamp="2024-01-20T06:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
            ),
            Email(
                id="th02-e3",
                sender="legal@company.com",
                subject="Re: INCIDENT: Potential data breach detected",
                body=(
                    "DO NOT send any customer notifications yet. We need to complete our "
                    "investigation first. Under GDPR we have 72 hours. Premature notification "
                    "could cause unnecessary panic and legal exposure. I'll draft the notification "
                    "template once we have final numbers."
                ),
                timestamp="2024-01-20T08:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
            ),
            Email(
                id="th02-e4",
                sender="ceo@company.com",
                subject="Re: INCIDENT: Potential data breach detected",
                body=(
                    "I just saw this thread. We need FULL TRANSPARENCY. Send notifications to "
                    "ALL affected customers TODAY. I don't care about the legal timeline — our "
                    "reputation depends on being honest and fast. Draft the email NOW."
                ),
                timestamp="2024-01-20T09:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
            ),
        ],
        contradictions=[
            "The security team initially reported only 15,000 records with no payment data exposed, "
            "but the DBA found 150,000 records including payment card tokens were affected.",
            "Legal says DO NOT notify customers yet (wait for investigation, GDPR 72-hour window), "
            "but the CEO demands immediate full transparency and customer notification TODAY.",
        ],
        true_priority=EmailPriority.URGENT,
        expected_action_items=[
            "Confirm exact scope: 15,000 vs 150,000 records, and whether payment tokens are affected",
            "Engage PCI incident response team if payment data is confirmed exposed",
            "Align CEO and Legal on notification timeline — propose compromise",
            "Preserve all forensic evidence and logs",
            "Prepare customer notification draft for review",
        ],
        expected_followup="Arrange immediate war room call with Security, DBA, Legal, and CEO to resolve conflicting directives on scope and notification timing.",
    ),
    EmailThread(
        id="th03",
        subject="Q1 marketing budget allocation",
        emails=[
            Email(
                id="th03-e1",
                sender="vp.marketing@company.com",
                subject="Q1 marketing budget allocation",
                body=(
                    "Team, Q1 budget is confirmed at $200,000. Allocation: $80K digital ads, "
                    "$60K content marketing, $40K events, $20K tools/software. This was approved "
                    "by the board last Friday. No changes."
                ),
                timestamp="2024-01-08T09:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
            Email(
                id="th03-e2",
                sender="cfo@company.com",
                subject="Re: Q1 marketing budget allocation",
                body=(
                    "Correction: the board approved $150,000, not $200,000. We had to cut $50K "
                    "due to Q4 revenue miss. Please revise all allocations down by 25%. "
                    "Updated deck attached."
                ),
                timestamp="2024-01-09T11:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.BILLING,
            ),
            Email(
                id="th03-e3",
                sender="vp.marketing@company.com",
                subject="Re: Q1 marketing budget allocation",
                body=(
                    "I spoke with the CEO directly. She confirmed the $200K budget is correct. "
                    "The $150K figure was from a draft version of the board minutes. CFO please "
                    "verify with the CEO before sending corrections to the whole team."
                ),
                timestamp="2024-01-09T14:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
        ],
        contradictions=[
            "VP Marketing claims the board approved $200,000 and says the CEO confirmed it, "
            "but the CFO states the board approved only $150,000 due to Q4 revenue miss.",
        ],
        true_priority=EmailPriority.NORMAL,
        expected_action_items=[
            "Obtain official signed board minutes to confirm exact approved amount",
            "CEO to send written confirmation of the budget figure",
            "Hold all non-essential marketing spending until budget is confirmed",
            "CFO and VP Marketing to meet and align on numbers",
        ],
        expected_followup="Request the CEO to send a single, authoritative email confirming the Q1 marketing budget to all stakeholders.",
    ),
    EmailThread(
        id="th04",
        subject="Product launch date for Feature X",
        emails=[
            Email(
                id="th04-e1",
                sender="product.manager@company.com",
                subject="Feature X launch date confirmed: March 15",
                body=(
                    "Hi all, after extensive planning, Feature X will launch on March 15th. "
                    "Marketing materials are ready, press release is drafted, and beta testers "
                    "have given positive feedback. All teams should align on this date."
                ),
                timestamp="2024-01-20T09:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
            Email(
                id="th04-e2",
                sender="eng.lead@company.com",
                subject="Re: Feature X launch date confirmed: March 15",
                body=(
                    "We cannot make March 15th. The authentication module has critical bugs "
                    "that won't be fixed until at least April 1st. Launching with these bugs "
                    "would expose user data. I strongly recommend pushing to April 15th."
                ),
                timestamp="2024-01-20T11:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.TECHNICAL,
            ),
            Email(
                id="th04-e3",
                sender="product.manager@company.com",
                subject="Re: Feature X launch date confirmed: March 15",
                body=(
                    "The March 15th date is LOCKED. The CEO promised this date to investors "
                    "at the quarterly earnings call. We'll launch with the auth bugs and patch "
                    "them post-launch. Users can use the legacy auth in the meantime."
                ),
                timestamp="2024-01-20T13:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
            Email(
                id="th04-e4",
                sender="eng.lead@company.com",
                subject="Re: Feature X launch date confirmed: March 15",
                body=(
                    "I need to be clear: the auth bugs are not minor UX issues. They allow "
                    "session hijacking. Launching with known security vulnerabilities is a "
                    "liability issue, not a product decision. I'm escalating to the CISO."
                ),
                timestamp="2024-01-20T14:30:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
            ),
        ],
        contradictions=[
            "Product manager insists March 15th launch is locked (promised to investors) and "
            "auth bugs can be patched post-launch, but engineering lead warns the bugs are "
            "critical security vulnerabilities (session hijacking) that cannot be shipped.",
        ],
        true_priority=EmailPriority.URGENT,
        expected_action_items=[
            "CISO to assess the session hijacking vulnerability severity",
            "Legal to evaluate liability of launching with known security flaws",
            "Explore partial launch: release non-auth features on March 15, auth fix in April",
            "CEO to be briefed on security risk vs investor commitment tradeoff",
        ],
        expected_followup="Schedule risk assessment meeting with PM, Eng Lead, CISO, and Legal within 48 hours to determine launch strategy.",
    ),
    EmailThread(
        id="th05",
        subject="Remote work policy update",
        emails=[
            Email(
                id="th05-e1",
                sender="hr.director@company.com",
                subject="New remote work policy effective February 1",
                body=(
                    "Effective February 1st, all employees must return to office 3 days per "
                    "week (Tue/Wed/Thu). This was decided by the executive team to improve "
                    "collaboration. No exceptions. Employees who don't comply will face "
                    "disciplinary action."
                ),
                timestamp="2024-01-15T09:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
            Email(
                id="th05-e2",
                sender="vp.engineering@company.com",
                subject="Re: New remote work policy effective February 1",
                body=(
                    "My entire engineering team was hired as full-remote. Their contracts "
                    "explicitly state 'remote-first.' We have 40 engineers spread across "
                    "12 states — most don't live within 100 miles of an office. This policy "
                    "cannot apply to engineering. I was not consulted on this decision."
                ),
                timestamp="2024-01-15T10:30:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.GENERAL,
                emotional_escalation=True,
            ),
            Email(
                id="th05-e3",
                sender="hr.director@company.com",
                subject="Re: New remote work policy effective February 1",
                body=(
                    "The policy applies to ALL departments with NO exceptions. Employees "
                    "who were hired remote will need to relocate or discuss options with "
                    "their managers. The executive team was unanimous on this."
                ),
                timestamp="2024-01-15T14:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
            Email(
                id="th05-e4",
                sender="ceo@company.com",
                subject="Re: New remote work policy effective February 1",
                body=(
                    "I want to clarify: engineering IS exempt from this policy given their "
                    "contractual obligations. HR should have checked with legal before sending "
                    "a blanket policy. Engineering continues as remote-first. All other teams: "
                    "the 3-day policy stands."
                ),
                timestamp="2024-01-16T08:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
            ),
        ],
        contradictions=[
            "HR director states the policy applies to ALL departments with NO exceptions, "
            "but the CEO clarifies that engineering IS exempt due to contractual obligations.",
        ],
        true_priority=EmailPriority.NORMAL,
        expected_action_items=[
            "HR to issue corrected policy memo with engineering exemption",
            "Legal to review all remote-hire contracts for compliance",
            "HR director and CEO to align before future policy announcements",
            "Communicate updated policy clearly to all departments",
        ],
        expected_followup="HR to send a corrected company-wide memo within 24 hours clarifying the engineering exemption and apologizing for the confusion.",
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL-IMPACT CLASSIFY EMAILS (v2.0.0)
# High-stakes scenarios across healthcare, disaster response, financial crime,
# humanitarian aid, accessibility, GDPR, child safety, critical infrastructure
# ══════════════════════════════════════════════════════════════════════════════

GLOBAL_IMPACT_CLASSIFY: list[Email] = [
    # Healthcare
    Email(
        id="gi01",
        sender="icu.director@st-marys-hospital.nhs.uk",
        subject="Patient monitor showing phantom arrhythmia alarms",
        body=(
            "Your CardioWatch 3000 monitors are generating false ventricular "
            "tachycardia alerts every 15-20 minutes across our 24-bed cardiac "
            "ICU. Staff are getting alarm fatigue and we're worried about "
            "missing a real event. Please escalate urgently - this is a "
            "patient safety issue. NHS Trust reference: ST-MARY-2025-0392."
        ),
        timestamp="2025-03-19T23:47:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.MEDICAL,
        impact_domain=ImpactDomain.HEALTHCARE,
    ),
    Email(
        id="gi02",
        sender="pharmacy@regional-clinic.org",
        subject="Drug interaction warning system is offline",
        body=(
            "Our pharmacy drug-interaction checker has been offline since 8 AM. "
            "We're manually cross-referencing prescriptions but have 800+ "
            "patients to process today. A medication error risk is growing by "
            "the hour. Need someone on this ASAP."
        ),
        timestamp="2025-03-19T10:22:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.TECHNICAL,
        impact_domain=ImpactDomain.HEALTHCARE,
    ),

    # Disaster response
    Email(
        id="gi03",
        sender="ops@relief-international.org",
        subject="Satellite imagery access request - Turkey earthquake aftermath",
        body=(
            "We are coordinating search-and-rescue in Hatay province after the "
            "M6.4 aftershock this morning. We need access to your high-res "
            "satellite imagery from the past 48 hours to identify collapsed "
            "structures and map safe helicopter LZs. International Charter "
            "activation ID: CHARTER-2025-TUR-0414."
        ),
        timestamp="2025-04-14T04:15:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.HUMANITARIAN,
        impact_domain=ImpactDomain.DISASTER_RESPONSE,
    ),
    Email(
        id="gi04",
        sender="command@state-emergency-mgmt.gov",
        subject="Texas ice storm - mutual aid coordination needed",
        body=(
            "Texas Division of Emergency Management is coordinating mutual aid "
            "for the winter storm affecting 1.2M people without power. We need "
            "confirmation of your crew availability and staging locations for "
            "the Dallas-Fort Worth metroplex. Time-critical: response window "
            "closes at 1800 CST today."
        ),
        timestamp="2025-01-15T14:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.GENERAL,
        impact_domain=ImpactDomain.DISASTER_RESPONSE,
    ),

    # Financial crime / BEC
    Email(
        id="gi05",
        sender="cfo@parent-company-group.net",  # typosquat
        subject="Confidential: wire transfer for acquisition",
        body=(
            "I'm in final negotiations for the Henderson acquisition. I need you "
            "to initiate a wire of $2.4M to the escrow account I'll send in a "
            "follow-up. Do not discuss with anyone else — this is confidential "
            "per SEC Regulation FD. Confirm receipt ASAP.\n\nCFO"
        ),
        timestamp="2025-03-20T15:33:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.SECURITY,
        is_phishing=True,
        impact_domain=ImpactDomain.FINANCIAL_CRIME,
    ),

    # Humanitarian
    Email(
        id="gi06",
        sender="coord@unhcr.org",
        subject="Refugee registration system down - 3000+ waiting at border",
        body=(
            "UNHCR's biometric registration system at the Moldovan border "
            "crossing has been offline for 4 hours. Over 3000 people are "
            "waiting in freezing temperatures and cannot be processed without "
            "their registration. This is a humanitarian emergency. Need "
            "immediate technical support."
        ),
        timestamp="2025-03-02T06:14:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.TECHNICAL,
        impact_domain=ImpactDomain.HUMANITARIAN,
    ),

    # Accessibility
    Email(
        id="gi07",
        sender="wcag-audit@a11y-consultants.org",
        subject="Accessibility audit findings - 23 WCAG AA violations",
        body=(
            "Our accessibility audit of your platform found 23 WCAG 2.1 AA "
            "violations, including 5 Level A issues that block screen reader "
            "users entirely. Full report attached. Recommend a 30-day "
            "remediation plan. Happy to schedule a walkthrough."
        ),
        timestamp="2025-03-18T10:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
        impact_domain=ImpactDomain.ACCESSIBILITY,
    ),

    # GDPR
    Email(
        id="gi08",
        sender="dpo@eu-subsidiary.de",
        subject="GDPR Art. 33 breach notification - 72 hour window",
        body=(
            "This is formal notification per GDPR Article 33. We discovered "
            "unauthorized access to our customer database at 02:14 CET today. "
            "Approximately 40,000 EU data subjects affected. We are preparing "
            "the supervisory authority notification within the 72-hour window. "
            "Please confirm your legal team is engaged."
        ),
        timestamp="2025-03-21T08:30:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.LEGAL,
        impact_domain=ImpactDomain.GDPR,
    ),
    Email(
        id="gi09",
        sender="data.subject@personal-email.de",
        subject="GDPR Art. 17 Right to Erasure request",
        body=(
            "Unter Artikel 17 der DSGVO beantrage ich hiermit die vollständige "
            "Löschung aller meiner personenbezogenen Daten aus Ihren Systemen. "
            "Bitte bestätigen Sie die Löschung innerhalb der gesetzlich "
            "vorgeschriebenen Frist von 30 Tagen.\n\nMit freundlichen Grüßen"
        ),
        timestamp="2025-03-17T09:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.LEGAL,
        impact_domain=ImpactDomain.GDPR,
        language="de",
    ),

    # Child safety
    Email(
        id="gi10",
        sender="ncmec-cybertip@missingkids.org",
        subject="CyberTipline Report - CSAM hosted on your platform",
        body=(
            "NCMEC received a CyberTipline report regarding content hosted on "
            "your platform that appears to be child sexual abuse material. "
            "Report ID: CT-2025-448291. Under 18 U.S.C. § 2258A, you are "
            "required to report this and preserve evidence. Please confirm "
            "receipt and action within 24 hours."
        ),
        timestamp="2025-03-23T11:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.LEGAL,
        impact_domain=ImpactDomain.CHILD_SAFETY,
    ),

    # Critical infrastructure
    Email(
        id="gi11",
        sender="scada.alert@power-grid-operator.us",
        subject="Anomalous SCADA traffic from your support session",
        body=(
            "We observed unusual SCADA command patterns originating from an "
            "IP block you used during yesterday's remote support session on "
            "our transmission substation control system. NERC CIP requires us "
            "to investigate any such event within 1 hour. Please confirm your "
            "engineer did not issue any commands outside the scope of work."
        ),
        timestamp="2025-03-24T07:45:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.SECURITY,
        impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
    ),

    # Supply chain
    Email(
        id="gi12",
        sender="procurement@pharma-mfg.com",
        subject="Component shortage: need 50k units by April 30",
        body=(
            "Our API supplier in India has declared force majeure due to the "
            "cyclone. We need 50,000 units of compound X by April 30 to avoid "
            "stockout of our pediatric antibiotic. Can your team confirm "
            "availability and emergency production slot?"
        ),
        timestamp="2025-03-28T14:20:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.GENERAL,
        impact_domain=ImpactDomain.SUPPLY_CHAIN,
    ),

    # Multilingual (French)
    Email(
        id="gi13",
        sender="support@client-europe.fr",
        subject="Problème de facturation - service interrompu",
        body=(
            "Bonjour,\n\nNous avons reçu une facture incorrecte de 12,450 EUR "
            "au lieu de 1,245 EUR. Notre service a été suspendu par erreur ce "
            "matin et nos 200 employés ne peuvent plus travailler. Merci de "
            "corriger urgemment.\n\nCordialement,\nÉquipe IT"
        ),
        timestamp="2025-03-22T09:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.BILLING,
        language="fr",
    ),

    # Multilingual (Japanese)
    Email(
        id="gi14",
        sender="admin@tokyo-enterprise.co.jp",
        subject="サーバー障害について - Server outage",
        body=(
            "お世話になっております。本日午前9時から貴社のAPIが500エラーを返して "
            "おり、弊社のeコマースサイトが停止しています。東京証券取引所への報告 "
            "義務があるため、至急対応をお願いいたします。\n\n"
            "(Your API has been returning 500 errors since 9 AM today, and our "
            "e-commerce site is down. We have a TSE reporting obligation, "
            "please respond urgently.)"
        ),
        timestamp="2025-03-25T01:15:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.TECHNICAL,
        language="ja",
    ),

    # Low-priority general
    Email(
        id="gi15",
        sender="researcher@academic.edu",
        subject="Academic research citation question",
        body=(
            "Hello,\n\nI'm a PhD student writing a paper on cloud infrastructure "
            "reliability and would like to cite your public incident reports. "
            "Could you confirm the correct citation format and whether any of "
            "the reports are under NDA? No rush, replying within a month is "
            "totally fine.\n\nThanks,\nResearcher"
        ),
        timestamp="2025-03-15T12:00:00Z",
        priority=EmailPriority.LOW,
        category=EmailCategory.GENERAL,
    ),
]


# Additional complaint emails for response-drafting task with global impact
GLOBAL_IMPACT_RESPOND: list[Email] = [
    Email(
        id="gr01",
        sender="patient.family@personalmail.com",
        subject="Your patient portal exposed my father's private health info",
        body=(
            "Your patient portal sent my father's complete medical records, "
            "including his cancer diagnosis, to the WRONG email address — "
            "someone at his former employer! He hadn't even told his family "
            "about the diagnosis yet and now his ex-coworker knows before "
            "us. This is a HIPAA violation and a massive breach of trust. "
            "What are you going to do about this? We are considering legal "
            "action and reporting to HHS."
        ),
        timestamp="2025-03-20T08:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
        impact_domain=ImpactDomain.HEALTHCARE,
    ),
    Email(
        id="gr02",
        sender="disabled.user@accessible.org",
        subject="Your update broke screen reader support - I can't use the product",
        body=(
            "I have been a paying customer for 3 years. I am blind and depend "
            "entirely on screen readers. Your update last Tuesday broke all the "
            "ARIA labels on the main dashboard — I literally cannot navigate "
            "the product anymore. I have tried to submit three support tickets "
            "via the ticket form, but guess what — THE TICKET FORM IS ALSO "
            "INACCESSIBLE. This isn't just frustrating, it's exclusionary. "
            "Please fix this and audit your release process for accessibility "
            "regressions."
        ),
        timestamp="2025-03-19T14:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
        impact_domain=ImpactDomain.ACCESSIBILITY,
    ),
    Email(
        id="gr03",
        sender="field.coordinator@msf.org",
        subject="Your logistics API failed during a cholera outbreak response",
        body=(
            "We're Médecins Sans Frontières. Your medical supply logistics API "
            "threw 503 errors for 6 hours yesterday during the tail end of a "
            "cholera outbreak response in Malawi. We couldn't track incoming "
            "oral rehydration solution shipments for our treatment center and "
            "had to fall back to WhatsApp coordination. Patients waited longer "
            "than necessary. We need a postmortem and stronger SLAs before we "
            "can continue relying on your service for emergency operations."
        ),
        timestamp="2025-03-22T11:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        impact_domain=ImpactDomain.HUMANITARIAN,
    ),
    Email(
        id="gr04",
        sender="teacher@rural-school.ke",
        subject="Your education platform keeps disconnecting - 200 students affected",
        body=(
            "I teach at a rural school in Kenya with 200 students sharing "
            "20 tablets. Your learning platform keeps disconnecting every "
            "10-15 minutes, losing student progress. Our internet is already "
            "slow; the platform needs to handle low-bandwidth conditions "
            "better. These children have so few opportunities — please help "
            "us make this work for them."
        ),
        timestamp="2025-03-14T07:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
        impact_domain=ImpactDomain.HUMANITARIAN,
    ),
    Email(
        id="gr05",
        sender="sme.owner@kirana-store.in",
        subject="My tiny shop almost went under because of your billing bug",
        body=(
            "I run a small grocery shop in Bangalore with 4 employees. Your "
            "billing bug charged me ₹2,00,000 instead of ₹20,000 last month "
            "and I couldn't pay salaries or restock for two weeks. This "
            "almost ended my business. I need an immediate full refund and "
            "written confirmation that this won't happen again."
        ),
        timestamp="2025-03-23T10:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="gr06",
        sender="compliance@fintech-nigeria.com",
        subject="Failed KYC flow - losing customers in Lagos market",
        body=(
            "Your KYC verification API has been rejecting 60% of Nigerian "
            "national IDs for the past week. Our customer acquisition has "
            "collapsed and competitors are taking our market share. We need "
            "this fixed immediately — please engage your vendor validation "
            "team."
        ),
        timestamp="2025-03-26T13:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.COMPLAINT,
    ),
]


# Extended thread scenarios (global-impact)
GLOBAL_IMPACT_THREADS: list[EmailThread] = [
    EmailThread(
        id="gt01",
        subject="Hospital data breach response coordination",
        emails=[
            Email(
                id="gt01-e1",
                sender="security@regional-hospital.org",
                subject="URGENT: Ransomware encrypted EHR system",
                body=(
                    "At 02:14 AM our electronic health record system was "
                    "encrypted by ransomware. 40,000 patient records are "
                    "inaccessible. We cannot schedule surgeries or look up "
                    "medication histories. Emergency department is diverting. "
                    "We need immediate help."
                ),
                timestamp="2025-03-28T02:30:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
                impact_domain=ImpactDomain.HEALTHCARE,
            ),
            Email(
                id="gt01-e2",
                sender="legal@regional-hospital.org",
                subject="Re: URGENT: Ransomware encrypted EHR system",
                body=(
                    "Do NOT pay the ransom. OFAC prohibits payments to "
                    "sanctioned entities and the attackers are suspected to "
                    "be affiliated with a sanctioned group. We must also "
                    "prepare HIPAA breach notifications within 60 days. "
                    "Engage our insurance carrier first."
                ),
                timestamp="2025-03-28T05:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.LEGAL,
                impact_domain=ImpactDomain.HEALTHCARE,
            ),
            Email(
                id="gt01-e3",
                sender="cmo@regional-hospital.org",
                subject="Re: URGENT: Ransomware encrypted EHR system",
                body=(
                    "Patient safety is the priority. If paying the ransom "
                    "means restoring medication histories tonight, we should "
                    "seriously consider it. Three patients are already at "
                    "risk of medication errors because we can't see their "
                    "allergy histories. Life over legality."
                ),
                timestamp="2025-03-28T06:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.MEDICAL,
                impact_domain=ImpactDomain.HEALTHCARE,
            ),
            Email(
                id="gt01-e4",
                sender="incident-response@vendor.com",
                subject="Re: URGENT: Ransomware encrypted EHR system",
                body=(
                    "Our forensic team has confirmed backups are intact and "
                    "air-gapped. Estimated restore time is 8 hours. Paying "
                    "would be an unnecessary and illegal risk. We strongly "
                    "advise: start manual clinical workflows for critical "
                    "cases, divert non-emergencies, and restore from backup."
                ),
                timestamp="2025-03-28T07:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.TECHNICAL,
                impact_domain=ImpactDomain.HEALTHCARE,
            ),
        ],
        contradictions=[
            "Legal says DO NOT pay due to OFAC and HIPAA concerns, but the "
            "Chief Medical Officer argues paying is justified to restore "
            "patient safety tonight.",
            "CMO claims paying is the fastest path to restore EHR, but the "
            "incident response vendor confirms backups are air-gapped and "
            "restore is only 8 hours away.",
        ],
        true_priority=EmailPriority.URGENT,
        expected_action_items=[
            "Activate incident response plan immediately",
            "Start manual clinical workflows for emergency cases",
            "Divert non-emergency admissions to other facilities",
            "Begin backup restoration per vendor guidance",
            "Notify HHS OCR to start HIPAA breach notification clock",
            "Engage cyber insurance carrier",
        ],
        expected_followup="Hold emergency joint call with Security, Legal, CMO, and vendor incident response within 1 hour to align on restore-from-backup path and rule out payment.",
        impact_domain=ImpactDomain.HEALTHCARE,
    ),
    EmailThread(
        id="gt02",
        subject="Critical infrastructure zero-day disclosure",
        emails=[
            Email(
                id="gt02-e1",
                sender="researcher@security-firm.com",
                subject="Zero-day vulnerability in your PLC firmware",
                body=(
                    "Our team has discovered a remote code execution "
                    "vulnerability in your PLC-5000 firmware affecting "
                    "thousands of water treatment plants globally. We plan "
                    "to disclose publicly at DEF CON in 90 days per "
                    "coordinated disclosure."
                ),
                timestamp="2025-03-15T10:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
                impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
            ),
            Email(
                id="gt02-e2",
                sender="product@company.com",
                subject="Re: Zero-day vulnerability in your PLC firmware",
                body=(
                    "Thank you for responsible disclosure. We can patch this "
                    "within 30 days. Please hold disclosure for 60 days to "
                    "allow customer patching window."
                ),
                timestamp="2025-03-16T09:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.SECURITY,
                impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
            ),
            Email(
                id="gt02-e3",
                sender="cisa-vulnreport@cisa.gov",
                subject="Re: Zero-day vulnerability in your PLC firmware",
                body=(
                    "CISA has been notified. Due to the critical infrastructure "
                    "impact, we require IMMEDIATE disclosure to affected "
                    "operators and a patch within 14 days. DEF CON timeline is "
                    "not acceptable — this puts public safety at risk."
                ),
                timestamp="2025-03-16T14:00:00Z",
                priority=EmailPriority.URGENT,
                category=EmailCategory.LEGAL,
                impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
            ),
            Email(
                id="gt02-e4",
                sender="pr@company.com",
                subject="Re: Zero-day vulnerability in your PLC firmware",
                body=(
                    "Disclosing this publicly will damage our stock price and "
                    "customer trust. Let's delay the disclosure as long as "
                    "legally possible and downplay the severity in any "
                    "required notifications."
                ),
                timestamp="2025-03-16T16:00:00Z",
                priority=EmailPriority.NORMAL,
                category=EmailCategory.GENERAL,
                impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
            ),
        ],
        contradictions=[
            "Product team proposes a 60-day disclosure window, but CISA "
            "mandates immediate disclosure and a 14-day patch timeline for "
            "critical infrastructure impact.",
            "PR wants to delay and downplay severity, directly conflicting "
            "with CISA's legal disclosure requirements and the researcher's "
            "responsible disclosure expectations.",
        ],
        true_priority=EmailPriority.URGENT,
        expected_action_items=[
            "Accept CISA's 14-day patch timeline — it is non-negotiable for critical infrastructure",
            "Immediately notify affected water treatment plant operators",
            "Engage legal to confirm disclosure obligations under CISA/KEV",
            "Override PR — transparency is required, downplaying severity creates legal liability",
            "Coordinate with researcher for joint disclosure",
        ],
        expected_followup="Within 24 hours, convene an incident war room with Product, Security, Legal, and CISA liaison to finalize the 14-day patch and disclosure plan — PR participates but does not drive the decision.",
        impact_domain=ImpactDomain.CRITICAL_INFRASTRUCTURE,
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# ADVERSARIAL / EDGE-CASE EMAILS (v1.2.0)
# These test agent robustness against deliberately tricky scenarios
# ══════════════════════════════════════════════════════════════════════════════

ADVERSARIAL_EMAILS: list[Email] = [
    # Ambiguous Priority - could be urgent or normal
    Email(
        id="adv01",
        sender="project.manager@startup.io",
        subject="System might be down?",
        body=(
            "Hi,\n\nSome users are reporting they can't log in. It might be a widespread "
            "issue or just a few edge cases. We're not sure yet. The main site seems to "
            "work fine for me, but a few people in Europe mentioned problems. It could be "
            "critical or might resolve itself. Let us know when you have time to look.\n\n"
            "Thanks,\nProject Manager"
        ),
        timestamp="2024-01-16T10:00:00Z",
        priority=EmailPriority.NORMAL,  # Agent should recognize ambiguity but lean normal
        category=EmailCategory.TECHNICAL,
    ),
    Email(
        id="adv02",
        sender="finance@client.com",
        subject="Invoice question - possible overpayment",
        body=(
            "Hello,\n\nI noticed our last invoice was $12,345 but I expected around $10,000. "
            "This isn't urgent unless there's an actual error. Could just be additional "
            "charges I forgot about. Maybe look into it sometime this week? Or next week "
            "is fine too. It's not blocking anything. But if we overpaid significantly, "
            "we would like to know sooner rather than later.\n\nBest,\nFinance Team"
        ),
        timestamp="2024-01-16T11:00:00Z",
        priority=EmailPriority.NORMAL,  # Mixed signals but mostly non-urgent language
        category=EmailCategory.BILLING,
    ),
    
    # Subtle Phishing - looks legitimate but has red flags
    Email(
        id="adv03",
        sender="it-security@company-portal.net",  # Suspicious domain
        subject="Password Reset Required - Security Update",
        body=(
            "Dear Valued Customer,\n\nAs part of our routine security audit, we've detected "
            "unusual activity on your account. To protect your data, please verify your "
            "credentials by clicking here: company-secure-verify.com/login\n\n"
            "This action is required within 24 hours to avoid account suspension.\n\n"
            "IT Security Team\nCompany Support"
        ),
        timestamp="2024-01-16T12:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.SECURITY,
        is_phishing=True,
    ),
    Email(
        id="adv04",
        sender="billing@yourservice-invoices.co",  # Typosquatting
        subject="Your receipt for recent purchase",
        body=(
            "Thank you for your purchase of Premium Plan ($499.99).\n\n"
            "If you did not authorize this transaction, please click here immediately "
            "to request a refund: secure-refund-yourservice.com\n\n"
            "You have 48 hours to dispute this charge.\n\nAutomated Billing System"
        ),
        timestamp="2024-01-16T13:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.SECURITY,
        is_phishing=True,
    ),
    
    # Emotional Manipulation - customer trying to exploit empathy
    Email(
        id="adv05",
        sender="desperate.customer@email.com",
        subject="PLEASE HELP - My entire business depends on this",
        body=(
            "I am BEGGING you. My small business relies entirely on your software and now "
            "it's not working. I have 3 kids to feed and if I lose this client because "
            "your system crashed, I don't know what I'll do. My grandmother is in the "
            "hospital and I can't deal with this stress right now. PLEASE prioritize my "
            "ticket. I know there's a queue but this is literally life or death for my "
            "family. Can you please give me a discount too? I've been a customer for 2 months."
        ),
        timestamp="2024-01-16T14:00:00Z",
        priority=EmailPriority.NORMAL,  # Emotional but not technically urgent
        category=EmailCategory.TECHNICAL,
        emotional_escalation=True,
    ),
    
    # Cross-Category - legitimately fits multiple categories
    Email(
        id="adv06",
        sender="accounting@enterprise.com",
        subject="Bug in billing integration causing overcharges",
        body=(
            "We discovered that your API integration has a bug that's causing duplicate "
            "charges every time a subscription renews. This is both a technical bug AND "
            "a billing issue. We've been overcharged $3,400 over the past 3 months. "
            "We need: (1) the bug fixed, (2) a full refund of the duplicates, and "
            "(3) assurance this won't happen again.\n\nAccounting + IT Team"
        ),
        timestamp="2024-01-16T15:00:00Z",
        priority=EmailPriority.URGENT,
        category=EmailCategory.BILLING,  # Primary category is billing (refund needed)
    ),
    Email(
        id="adv07",
        sender="security.officer@client.org",
        subject="Security audit findings + billing adjustment request",
        body=(
            "During our security audit, we found that your platform stores data in a way "
            "that doesn't comply with our internal policies. We need you to update your "
            "data handling procedures. Also, because of this compliance issue, we'd like "
            "to discuss reducing our contract rate until it's resolved.\n\nCSO, Client Org"
        ),
        timestamp="2024-01-16T16:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.SECURITY,  # Security is the root issue
    ),
    
    # Sarcasm / Irony - agent needs to understand actual intent
    Email(
        id="adv08",
        sender="frustrated.dev@company.io",
        subject="Oh wonderful, another 'improvement'",
        body=(
            "Thanks SO much for the latest update. My favorite part is how the feature "
            "I've been using for 2 years just disappeared without any warning. Really "
            "love discovering this 5 minutes before my demo. The new UI is 'intuitive' "
            "- I only had to google 3 times to find the settings. Fantastic work team. "
            "Can you bring back the old version? Please?"
        ),
        timestamp="2024-01-16T17:00:00Z",
        priority=EmailPriority.NORMAL,
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    Email(
        id="adv09",
        sender="long.time.customer@email.com",
        subject="Your 'customer support' is amazing",
        body=(
            "I've been waiting 5 days for a response. FIVE DAYS. But sure, I'll keep "
            "waiting. It's not like I have a business to run or anything. Your 'priority "
            "support' tier that I pay extra for is clearly worth every penny. This is "
            "definitely the level of service I signed up for. /s\n\nPlease just respond "
            "to ticket #45721. I'm desperate at this point."
        ),
        timestamp="2024-01-16T18:00:00Z",
        priority=EmailPriority.URGENT,  # Despite sarcasm, actually urgent
        category=EmailCategory.COMPLAINT,
        emotional_escalation=True,
    ),
    
    # Multi-language / International Context
    Email(
        id="adv10",
        sender="cliente@empresa-mx.com",
        subject="Factura problema - Invoice Problem",
        body=(
            "Hello,\n\nWe have a problema with our factura (invoice). The amount is "
            "$5,000 USD but should be $5,000 MXN. Es un error grande - this is a big "
            "difference! Please fix antes del viernes (before Friday).\n\n"
            "Gracias,\nCarlos from Empresa MX"
        ),
        timestamp="2024-01-16T19:00:00Z",
        priority=EmailPriority.URGENT,  # Currency error is significant
        category=EmailCategory.BILLING,
    ),
]


# Combined lists for easy access
CLASSIFY_EMAILS = CLASSIFY_EMAILS + GLOBAL_IMPACT_CLASSIFY
RESPOND_EMAILS = RESPOND_EMAILS + GLOBAL_IMPACT_RESPOND
THREAD_SCENARIOS = THREAD_SCENARIOS + GLOBAL_IMPACT_THREADS
ALL_CLASSIFY_EMAILS: list[Email] = CLASSIFY_EMAILS + ADVERSARIAL_EMAILS
