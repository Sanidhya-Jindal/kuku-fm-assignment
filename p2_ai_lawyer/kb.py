"""The ONLY legal facts the bot may state. Each fact was checked against a public source on 21 Nov 2026.
The model must cite fact IDs; code rejects any law, section or case that is not in a retrieved fact.
To add a topic: add facts with a source, re-run the tests. Never add a fact you have not checked."""

CHECKED_ON = "2026-11-21"

TOPICS = {
    "deposit": {"title": "Security deposit not returned by landlord", "other_side": "landlord",
                "keywords": ["deposit", "landlord", "rent", "flat", "pg", "tenant", "house owner", "makan malik",
                             "advance", "kiraya", "security", "jama", "किराया", "मकान मालिक", "जमा", "एडवांस"]},
    "consumer": {"title": "Refund / defective product / bad service", "other_side": "company",
                 "keywords": ["refund", "order", "amazon", "flipkart", "product", "defective", "warranty", "service",
                              "delivery", "replace", "customer care", "consumer", "booking", "airline", "flight",
                              "रिफंड", "ऑर्डर", "कंपनी", "टिकट"]},
    "wages": {"title": "Salary or wages not paid", "other_side": "employer",
              "keywords": ["salary", "wages", "employer", "company not paying", "hr", "tankhwah", "tankha",
                           "boss", "job", "full and final", "fnf", "stipend", "unpaid", "mazdoori", "सैलरी", "वेतन", "तनख्वाह"]},
    "cheque": {"title": "Cheque bounce", "other_side": "person who gave the cheque",
               "keywords": ["cheque", "check bounce", "bounced", "dishonour", "return memo", "insufficient funds", "चेक"]},
    "cyber": {"title": "Online / UPI fraud", "other_side": "",
              "keywords": ["fraud", "scam", "upi", "otp", "hacked", "money deducted", "phishing", "fake call",
                           "link", "cyber", "online thagi", "dhokha", "धोखा", "ठगी"]},
}

FACTS = [
    # Tenancy
    ("D1", "deposit", "Rent is a state subject. The Model Tenancy Act, 2021 is a model law that each state may adopt; it is not automatically in force in every state.",
     "https://www.deccanherald.com/opinion/model-tenancy-act-a-mixed-bag-1131814.html"),
    ("D2", "deposit", "Under the Model Tenancy Act, 2021, the security deposit may not exceed two months' rent for residential premises (six months for non-residential). This applies only where the state has adopted a law based on it.",
     "https://prsindia.org/billtrack/the-model-tenancy-act-2021"),
    ("D3", "deposit", "Under the Model Tenancy Act, 2021, the deposit is to be returned when the tenant hands back possession, after lawful deductions.",
     "https://www.business-standard.com/podcast/current-affairs/what-is-the-model-tenancy-act-122010400085_1.html"),
    ("D4", "deposit", "Practical route: keep the rent agreement, rent payment proof, deposit payment proof and move-out photos; send a written demand (or legal notice); if still unpaid, a money recovery claim can be filed in the local civil court, or before the rent authority/court where the state has one.",
     "general guidance"),
    # Consumer
    ("C1", "consumer", "The Consumer Protection Act, 2019 lets a consumer complain about defective goods, deficient services and unfair trade practices, including purchases from e-commerce platforms. Goods bought for commercial resale are excluded.",
     "https://righttoinformation.wiki/consumer-court-how-to-file-india"),
    ("C2", "consumer", "The National Consumer Helpline (call 1915 or consumerhelpline.gov.in) is a free first step: it takes the complaint to the company and tries to settle it.",
     "https://righttoinformation.wiki/complaints/consumer-complaint-edaakhil"),
    ("C3", "consumer", "A formal complaint goes to the District Consumer Commission if the value of goods or services paid does not exceed Rs 50 lakh; Rs 50 lakh to Rs 2 crore goes to the State Commission; above Rs 2 crore to the National Commission.",
     "https://taxguru.in/?p=800045"),
    ("C4", "consumer", "Section 69 of the Consumer Protection Act, 2019: a complaint must be filed within two years from the date the cause of action arose. Late filing needs a reason the commission accepts.",
     "https://righttoinformation.wiki/consumer-court-how-to-file-india"),
    ("C5", "consumer", "Complaints can be filed online on the consumer commissions' e-filing portal (e-Daakhil / e-Jagriti). You can file and argue your own case; a lawyer is optional. Filing fees are nil or small for low-value claims; check the current fee table on the portal.",
     "https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/mar/doc2025314520301.pdf"),
    # Wages
    ("W1", "wages", "The four Labour Codes, including the Code on Wages, 2019, came into force on 21 November 2025, replacing 29 older labour laws. Some rules are being rolled out in phases.",
     "https://labour.gov.in/sites/default/files/pib2192463.pdf"),
    ("W2", "wages", "Under the Labour Codes, workers can raise wage claims for up to 3 years.",
     "https://labour.gov.in/sites/default/files/pib2192463.pdf"),
    ("W3", "wages", "The Labour Codes require timely payment of wages and appointment letters for workers.",
     "https://indiantelevision.com/news-headline/early-gratuity-wfh-provision-gender-neutral-wages-centre-enacts-new-labour-codes-251122/"),
    ("W4", "wages", "Practical route: ask for the salary in writing (email) and keep the offer/appointment letter, payslips, attendance and bank statements; complain to the state Labour Department; send a legal notice. Senior or managerial staff may need a civil claim instead, so confirm the right route with a lawyer or the labour office.",
     "general guidance"),
    # Cheque
    ("Q1", "cheque", "Under Section 138 of the Negotiable Instruments Act, 1881, a bounced cheque can be a criminal offence, punishable with up to two years in prison or a fine up to twice the cheque amount.",
     "https://blog.ipleaders.in/?p=128955"),
    ("Q2", "cheque", "For a Section 138 case, a written demand notice must be sent to the person who gave the cheque within 30 days of getting the bank's return memo.",
     "https://www.legalserviceindia.com/Legal-Articles/?p=35933"),
    ("Q3", "cheque", "After receiving the notice, the person who gave the cheque has 15 days to pay.",
     "https://www.legalserviceindia.com/Legal-Articles/?p=35933"),
    ("Q4", "cheque", "If they do not pay within those 15 days, the complaint must be filed before the magistrate within one month (Section 142 of the Negotiable Instruments Act, 1881). A complaint filed before the 15 days end can be dismissed as premature.",
     "https://cdnbbsr.s3waas.gov.in/s3ec0369f268fb2ba1068615b3219c6e8f/uploads/2024/09/2024092355.pdf"),
    # Cyber fraud
    ("F1", "cyber", "Report financial cyber fraud immediately by calling 1930 or on the National Cyber Crime Reporting Portal, cybercrime.gov.in.",
     "https://en.wikipedia.org/wiki/National_Cybercrime_Reporting_Portal"),
    ("F2", "cyber", "Reporting within the first hours (the 'golden hour') gives the best chance of the money being frozen. A 1930 report is not an FIR and does not automatically reverse the payment; report even if time has passed.",
     "https://the420.in/?p=95060"),
    ("F3", "cyber", "Also tell your bank or wallet right away and block the card/UPI, and keep screenshots, transaction IDs and the fraudster's number.",
     "https://the420.in/?p=95060"),
    # Everyone
    ("G1", "all", "Free legal aid: call the NALSA helpline 15100 or visit the District Legal Services Authority. Under Section 12 of the Legal Services Authorities Act, 1987, women, children, SC/ST members and some other groups qualify regardless of income; others may qualify on income.",
     "https://nalsa.gov.in/services/legal-aid/eligibility?locale=ma"),
    ("G2", "all", "Legal Services Authorities also run Lok Adalats, where disputes can be settled by agreement.",
     "https://nalsa.gov.in/sites/default/files/document/PLA.pdf?locale=od"),
]

FACT = {f[0]: {"id": f[0], "topic": f[1], "text": f[2], "source": f[3]} for f in FACTS}


def facts_for(topic):
    return [f for f in FACT.values() if f["topic"] in (topic, "all")]
