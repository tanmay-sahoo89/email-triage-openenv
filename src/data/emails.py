"""Synthetic email datasets for all three tasks. 10+ emails each."""

from src.models import Email, EmailPriority, EmailCategory, EmailThread

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
