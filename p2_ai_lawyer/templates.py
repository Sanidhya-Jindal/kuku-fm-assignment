"""Documents are filled from fixed templates in code, so the legal wording never comes from the model.
Anything we do not know is left as [____] for the person to fill in."""
from datetime import date

B = "[____]"

REMEDY = {
    "deposit": "If the amount is not returned within the time given, I will be constrained to initiate appropriate legal proceedings for recovery of the amount with interest and costs, entirely at your risk as to costs.",
    "consumer": "If the matter is not resolved within the time given, I will file a complaint before the District Consumer Commission under the Consumer Protection Act, 2019, seeking a refund, compensation and costs.",
    "wages": "If my dues are not paid within the time given, I will approach the Labour Department / competent authority under the Code on Wages, 2019 and take any other legal steps available to me.",
    "cheque": "This notice is issued under Section 138 of the Negotiable Instruments Act, 1881. If you fail to pay the cheque amount within 15 days of receiving this notice, I will file a complaint against you before the competent Magistrate.",
}

ASK = {
    "deposit": "return my security deposit of Rs {amount}",
    "consumer": "refund Rs {amount} / replace the product / fix the service (choose what you want)",
    "wages": "pay my unpaid salary/wages of Rs {amount}",
    "cheque": "pay the cheque amount of Rs {amount}",
}


def _v(case, k):
    v = (case or {}).get(k)
    return str(v) if v not in (None, "", [], "unknown") else B


def legal_notice(topic, case):
    if topic not in REMEDY:
        return None
    c = case or {}
    facts = c.get("timeline") or []
    fact_lines = "\n".join(f"{i}. {e.get('date') or B}: {e.get('event', '')}" for i, e in enumerate(facts, 1)) or f"1. {B}"
    days = "15" if topic == "cheque" else "15 (fifteen)"
    cheque = ""
    if topic == "cheque":
        cheque = (f"\nCheque details: Cheque No. {B}, dated {B}, for Rs {_v(c, 'amount')}, drawn on {B} bank. "
                  f"It was returned unpaid on {B} with the reason \"{B}\" (bank return memo received on {B}).\n")
    return f"""DRAFT - check every detail before sending. Not reviewed by a lawyer.
Send by Speed Post / Registered Post with acknowledgement and keep the receipt. Email a copy too.

LEGAL NOTICE / DEMAND NOTICE

Date: {date.today().strftime('%d %B %Y')}

From: {_v(c, 'user_name')}
Address: {B}
Phone / Email: {B}

To: {_v(c, 'other_party')}
Address: {B}

Subject: Demand to {ASK[topic].format(amount=_v(c, 'amount'))}

Sir/Madam,

1. Facts:
{fact_lines}
{cheque}
2. Proof I have: {", ".join(c.get("evidence_have") or []) or B}

3. Despite my requests, you have not done so. I call upon you to {ASK[topic].format(amount=_v(c, 'amount'))} within {days} days of receiving this notice.

4. {REMEDY[topic]}

5. Please treat this as final notice before legal action.

{_v(c, 'user_name')}
(Signature)
"""


def fraud_report(case):
    c = case or {}
    return f"""DRAFT - for calling 1930 / filing at cybercrime.gov.in and for your bank. Fill every blank.

What happened (in short): {_v(c, 'what_happened')}
Date and time of each payment: {B}
Amount lost: Rs {_v(c, 'amount')}
Your bank / UPI app and account (last 4 digits only): {B}
Transaction / UTR IDs: {B}
Fraudster's phone number / UPI ID / link / website: {_v(c, 'other_party')}
Proof saved (screenshots, SMS, call log): {", ".join(c.get("evidence_have") or []) or B}

Bank letter: "I did not authorise transaction(s) {B} on {B} for Rs {B}. Please block my card/UPI, raise a fraud
dispute, and share the complaint reference number. I have reported it on 1930 (ref: {B})."
"""


def draft(topic, case):
    return fraud_report(case) if topic == "cyber" else legal_notice(topic, case)
