"""
Zodia Markets Configuration
Company-specific settings, registered jurisdictions, and regulatory focus areas
Tuned to Zodia's ACTUAL business model and the regulations that touch it.
"""

# ============================================================================
# ZODIA MARKETS COMPANY PROFILE - ACCURATE BUSINESS DESCRIPTION
# ============================================================================

COMPANY_NAME = "Zodia Markets"

COMPANY_DESCRIPTION = """
Zodia Markets is an institution-first digital asset marketplace and brokerage, 
backed by Standard Chartered (via SC Ventures) and OSL Group, designed to bridge 
the gap between traditional finance and digital assets.

PURPOSE: Founded to offer institutional-grade infrastructure for trading digital 
assets without compromising traditional finance standards.

BACKING: A partnership between Standard Chartered and BC Technology Group 
(parent of OSL), with FCA registration in the UK and entities in Ireland, 
Jersey, and Abu Dhabi (ADGM).

TARGET CLIENTS: Corporations, financial institutions, and professional investors 
ONLY. Zodia does NOT serve retail clients.
"""

# ============================================================================
# ZODIA MARKETS SPECIFIC BUSINESS ACTIVITIES
# These are the activities that TRIGGER regulatory requirements
# ============================================================================

ZODIA_BUSINESS_ACTIVITIES = {
    "otc_brokerage": {
        "name": "OTC Broker-Aided Facilitation",
        "description": "Over-the-counter trading where Zodia brokers facilitate large institutional trades (voice and electronic) in digital assets. Includes request-for-quote (RFQ) and negotiated execution.",
        "regulatory_triggers": [
            "Broker-dealer licensing",
            "VASP/CASP authorization",
            "Investment services licensing",
            "OTC derivatives regulation (if applicable)"
        ]
    },
    "electronic_spot_trading": {
        "name": "Order-Book Driven Electronic Spot Trading",
        "description": "Electronic exchange/matching engine for spot trading of digital assets. FIX API connectivity. 24/7 execution. High-speed, low-latency matching.",
        "regulatory_triggers": [
            "Exchange/trading platform licensing",
            "Multilateral trading facility (MTF) rules",
            "Organized trading facility (OTF) rules",
            "Market operator licensing"
        ]
    },
    "fiat_to_crypto": {
        "name": "Fiat-to-Crypto Conversion",
        "description": "Converting fiat currencies (USD, EUR, GBP, etc.) into digital assets (BTC, ETH, etc.). On-ramping institutional clients from traditional finance into crypto.",
        "regulatory_triggers": [
            "Payment services / e-money licensing",
            "Money transmission licensing",
            "Foreign exchange rules",
            "Currency exchange regulation"
        ]
    },
    "crypto_to_crypto": {
        "name": "Crypto-to-Crypto Trading",
        "description": "Exchange between different digital assets (e.g., BTC to ETH, stablecoin swaps). Includes stablecoin pairs.",
        "regulatory_triggers": [
            "Virtual asset exchange licensing",
            "VASP registration",
            "Securities rules (if token classified as security)"
        ]
    },
    "non_custodial_model": {
        "name": "Non-Custodial Trading Model",
        "description": "Zodia does NOT hold client assets directly. Uses a network of trusted third-party custodians (including Zodia Custody, a separate entity). Segregated client funds model - fiat held at Standard Chartered, digital assets at custodians.",
        "regulatory_triggers": [
            "Custody delegation rules",
            "Client asset protection rules",
            "Outsourcing / third-party risk rules",
            "Segregation of client funds requirements"
        ]
    },
    "cross_border_services": {
        "name": "Cross-Border Institutional Services",
        "description": "Serving institutional clients across multiple jurisdictions from Zodia's 4 licensed entities (UK, Ireland, ADGM, Jersey). Clients may be based in jurisdictions where Zodia is NOT licensed.",
        "regulatory_triggers": [
            "Cross-border financial services rules",
            "Reverse solicitation exemptions",
            "Direct market access rules",
            "Passporting (EU/MiCA from Ireland)",
            "Equivalence/recognition regimes"
        ]
    }
}

# Services offered
ZODIA_SERVICES = [
    "OTC (over-the-counter) broker-aided facilitation",
    "Order-book driven electronic spot execution",
    "Fiat-to-crypto on/off ramping (20+ fiat currencies)",
    "Crypto-to-crypto trading (70+ digital assets)",
    "Stablecoin trading and payments (USDC, USDT, EURC)",
    "Institutional-grade FIX API connectivity",
    "T+0 settlement for 95% of trades",
    "24/7 trading operations"
]

COMPANY_ENTITY_TYPE = "Virtual Asset Service Provider (VASP) / Digital Asset Broker-Dealer / Electronic Trading Platform"

# ============================================================================
# ZODIA MARKETS REGISTERED JURISDICTIONS & LICENSES
# ============================================================================

ZODIA_REGISTERED_JURISDICTIONS = {
    "United Kingdom": {
        "entity": "Zodia Markets (UK) Limited",
        "regulator": "Financial Conduct Authority (FCA)",
        "license_type": "Cryptoasset Registration (MLR)",
        "reference": "FRN 954558",
        "date_granted": "July 2022",
        "scope": "OTC trading, exchange services under Money Laundering Regulations",
        "status": "Active"
    },
    "Ireland": {
        "entity": "Zodia Markets (Ireland) Limited",
        "regulator": "Central Bank of Ireland (CBI)",
        "license_type": "VASP Registration",
        "reference": "VASP Registration",
        "date_granted": "October 2023",
        "scope": "OTC trading, exchange services to institutional clients; pathway to MiCA CASP authorization",
        "status": "Active"
    },
    "Abu Dhabi (ADGM)": {
        "entity": "Zodia Markets (AME) Limited",
        "regulator": "ADGM Financial Services Regulatory Authority (FSRA)",
        "license_type": "Financial Services Permission (FSP)",
        "reference": "FSP",
        "date_granted": "December 2024",
        "scope": "Regulated virtual asset brokerage",
        "status": "Active"
    },
    "Jersey": {
        "entity": "Zodia Markets (Jersey)",
        "regulator": "Jersey Financial Services Commission (JFSC)",
        "license_type": "Virtual Currency Exchange Business Registration",
        "reference": "JFSC Registration",
        "date_granted": "July 2024",
        "scope": "Virtual currency exchange business",
        "status": "Active"
    }
}

# EU jurisdictions relevant due to MiCA passporting from Ireland
ZODIA_EU_MICA_JURISDICTIONS = [
    "European Union",
    "Germany", "France", "Netherlands", "Italy", "Spain",
    "Belgium", "Luxembourg", "Austria", "Portugal", "Greece",
    "Finland", "Sweden", "Denmark", "Poland", "Czech Republic",
    "Hungary", "Romania", "Bulgaria", "Croatia", "Slovakia",
    "Slovenia", "Estonia", "Latvia", "Lithuania", "Malta", "Cyprus"
]

# All jurisdictions Zodia Markets operates in or may expand to
ZODIA_ALL_RELEVANT_JURISDICTIONS = list(ZODIA_REGISTERED_JURISDICTIONS.keys()) + ZODIA_EU_MICA_JURISDICTIONS + [
    "United Arab Emirates",
    "Singapore", "Hong Kong", "Japan", "South Korea",
    "Australia", "Canada", "Switzerland", "Liechtenstein",
    "Bermuda", "Cayman Islands", "British Virgin Islands",
    "Bahrain", "Saudi Arabia", "Qatar",
    "South Africa", "Nigeria", "Brazil", "India"
]

# ============================================================================
# REGULATORY FOCUS AREAS - SPECIFIC TO ZODIA'S BUSINESS
# ============================================================================

ZODIA_REGULATORY_FOCUS = [
    "VASP/CASP licensing and authorization for OTC brokerage",
    "Digital asset exchange/trading platform licensing",
    "Broker-dealer registration for crypto assets",
    "Cross-border digital asset services rules",
    "Reverse solicitation exemptions for crypto/virtual assets",
    "Direct market access for foreign crypto platforms",
    "Fiat-to-crypto gateway / payment services licensing",
    "AML/KYC requirements for institutional crypto clients",
    "Client asset segregation and custody delegation rules",
    "Stablecoin trading and settlement regulation",
    "MiCA CASP authorization and passporting",
    "Investment services / MiFID classification of crypto assets",
    "Sanctions screening for digital asset transactions"
]

# ============================================================================
# REGULATION STATUS FILTERS
# ============================================================================

REGULATION_STATUS_FILTER = [
    "enacted", "enforced", "final", "in force",
    "effective", "implemented", "gazetted", "promulgated"
]

REGULATION_STATUS_EXCLUDE = [
    "proposed", "draft", "consultation",
    "white paper", "discussion paper", "under review"
]

# ============================================================================
# ZODIA RESEARCH OUTPUT STRUCTURE
# ============================================================================

ZODIA_REPORT_SECTIONS = {
    "summary": "Concise overview of the country's regulatory regime as it applies to Zodia Markets serving INSTITUTIONAL clients only (corporations, banks, funds, professional investors) via OTC brokerage, electronic spot trading, fiat-to-crypto, and non-custodial digital asset services. State whether rules are primarily retail-focused or also catch institutional services.",
    "high_level_risk_points": "Key regulatory risks for Zodia Markets when serving INSTITUTIONAL clients only. Distinguish between risks that apply to all clients vs risks that are retail-specific and would NOT affect Zodia's institutional-only business.",
    "regulatory_framework": "The regulatory framework governing Zodia's activities for institutional clients: (a) OTC crypto brokerage to institutions, (b) electronic trading platforms for professional participants, (c) fiat-to-crypto for corporate clients, (d) custody delegation. Identify any institutional/professional client exemptions or carve-outs.",
    "virtual_asset_trading_platforms": "Licensing requirements for operating an electronic trading platform/exchange. Does the jurisdiction differentiate between platforms serving retail vs institutional clients? Are there lighter requirements for institutional-only platforms? MTF/OTF/market operator rules?",
    "stablecoin_regulation": "Stablecoin rules affecting institutional trading and settlement (USDC, USDT, EURC). Do stablecoin rules apply differently to institutional vs retail transactions?",
    "store_of_value_facility_rules": "Store of value facility, e-money, and payment token rules. Are institutional-to-institutional stablecoin transactions treated differently from retail?",
    "regulatory_expectations_and_licensing_triggers": "Map each of Zodia's activities to specific licensing triggers when the CLIENT is an INSTITUTION. Are there exemptions for institutional-only VASPs? Professional client carve-outs? Qualified investor thresholds?",
    "territorial_scope_and_perimeter_test": "CRITICAL PERIMETER TEST: (a) Does this jurisdiction's law apply based on where the PROVIDER is located or where the CLIENT is? Cite statutory language. (b) If Zodia has ZERO establishment, ZERO operational presence, ZERO solicitation - is it outside scope? (c) IMPORTANT: Does the scope analysis differ for institutional vs retail clients? Many laws aim to protect retail consumers - do they also catch foreign VASPs serving only institutions? (d) CONCLUSION: Can Zodia take the view it is outside the perimeter when serving only institutional clients with zero local presence?",
    "reverse_solicitation_and_direct_market_access": "REVERSE SOLICITATION FOR INSTITUTIONAL CLIENTS: (a) Is reverse solicitation recognized? In statute, regulation, or guidance? Cite source. (b) Is the exemption BROADER for institutional/professional clients? (Many jurisdictions have wider exemptions for institutions.) (c) Conditions when an institutional client initiates contact. Documentation? One-off or ongoing? (d) What breaks reverse solicitation? (e) Enforcement focus: does the regulator pursue foreign VASPs serving institutions, or mainly retail? (f) DIRECT MARKET ACCESS: Can institutional clients access Zodia's platform from UK/Ireland/ADGM/Jersey without local presence?",
    "cross_border_client_advisory": "Can Zodia serve an INSTITUTIONAL client from this jurisdiction? (a) With zero presence and institutional client approaching on own initiative - is Zodia outside scope? (b) Which Zodia entity best positioned? (c) EU/MiCA passporting available? (d) AML/KYC on foreign VASP or on the institutional client locally?",
    "compliance_guidance_and_recommendations": "Verdict for serving INSTITUTIONAL clients: (a) SERVE (OUTSIDE PERIMETER) - zero presence + institutional-only + reverse solicitation / SERVE VIA REVERSE SOLICITATION ONLY / SERVE VIA PASSPORTING / SERVE WITH CONDITIONS / DECLINE (b) Documentation and safeguards needed (c) Which Zodia entity? (d) What must Zodia NEVER do? (e) What triggers would bring Zodia into scope even for institutional services?",
    "sources_and_references": "List ALL regulations, laws, guidance documents, and regulatory publications cited in this report. For each: (a) Full official name, (b) Regulatory body/issuer, (c) Date enacted/effective, (d) URL to official source where the full text can be read. Include links to regulator websites, official gazettes, and government legal databases."
}

# ============================================================================
# CROSS-BORDER ADVISORY CONTEXT
# ============================================================================

ZODIA_LICENSED_ENTITIES_CONTEXT = """
Zodia Markets currently holds licenses/registrations in exactly 4 jurisdictions:

1. UNITED KINGDOM - Zodia Markets (UK) Limited
   - Regulator: FCA (Financial Conduct Authority)
   - License: Cryptoasset Registration under Money Laundering Regulations
   - FRN: 954558 | Granted: July 2022
   - Scope: OTC trading, exchange services
   - NOTE: UK FCA registration covers AML/KYC compliance, NOT full investment services authorization

2. IRELAND - Zodia Markets (Ireland) Limited
   - Regulator: Central Bank of Ireland (CBI)
   - License: VASP Registration
   - Granted: October 2023
   - Scope: OTC trading, exchange services; pathway to EU MiCA CASP authorization
   - NOTE: Under MiCA, once Zodia obtains full CASP authorization via Ireland,
     it can passport services across all 27 EU/EEA member states

3. ABU DHABI (ADGM) - Zodia Markets (AME) Limited
   - Regulator: ADGM Financial Services Regulatory Authority (FSRA)
   - License: Financial Services Permission (FSP)
   - Granted: December 2024
   - Scope: Regulated virtual asset brokerage
   - NOTE: ADGM is a financial free zone; this does NOT cover broader UAE (VARA/SCA)

4. JERSEY - Zodia Markets (Jersey)
   - Regulator: Jersey Financial Services Commission (JFSC)
   - License: Virtual Currency Exchange Business Registration
   - Granted: July 2024
   - Scope: Virtual currency exchange business

KEY FACTS:
- Zodia Markets does NOT hold licenses in any other jurisdiction
- Zodia Markets serves INSTITUTIONAL clients ONLY (corporations, financial institutions, professional investors)
- Zodia uses a NON-CUSTODIAL model (third-party custodians hold client assets)
- Zodia provides OTC brokerage AND electronic exchange/matching engine services
- Zodia handles fiat-to-crypto AND crypto-to-crypto transactions
"""

# ============================================================================
# ZODIA MARKETS CROSS-BORDER LEGAL APPROACH: THE PERIMETER TEST
# This is how Zodia's legal/compliance team evaluates whether a jurisdiction's
# law applies to them when they are NOT licensed there.
# ============================================================================

ZODIA_PERIMETER_TEST = """
ZODIA MARKETS' CROSS-BORDER LEGAL APPROACH - THE PERIMETER / TERRITORIAL SCOPE TEST:

Zodia Markets takes the following legal position for jurisdictions where it is NOT licensed:

As long as services are NOT provided "in or from within" the jurisdiction, Zodia may be 
OUTSIDE THE SCOPE of that jurisdiction's law and therefore NOT required to register or 
obtain a local license.

For this argument to hold, ALL of the following conditions must be met:

1. NO PERMANENT ESTABLISHMENT: Zodia has no registered entity, branch, subsidiary, or 
   corporate presence in the jurisdiction.

2. NO OPERATIONAL PRESENCE: Zodia has no office, employees, servers, agents, or 
   representatives physically located in the jurisdiction.

3. NO ACTIVE SOLICITATION: Zodia does NOT market, advertise, cold-call, or actively 
   solicit clients in or targeting the jurisdiction. No local-language websites, no 
   local advertising, no attendance at local events for marketing purposes.

4. PURELY REVERSE SOLICITATION: Zodia ONLY serves clients from that jurisdiction on 
   a REVERSE SOLICITATION basis - meaning the client approached Zodia entirely on 
   their OWN initiative, without any prompting, marketing, or solicitation by Zodia.

THE CRITICAL QUESTION FOR EACH JURISDICTION:
- Does the local law define its scope based on where the SERVICE is provided from, 
  or where the CLIENT is located?
- If the law catches "providing services TO persons in the jurisdiction" (client-location 
  test), Zodia may still be in scope even without local presence.
- If the law only catches "providing services IN or FROM the jurisdiction" (provider-location 
  test), Zodia's argument is stronger.
- Some jurisdictions have BOTH tests, or have expanded their scope to catch foreign 
  providers serving local clients.
- The analysis must determine which test the jurisdiction uses and whether Zodia's 
  "no presence + reverse solicitation only" model puts it outside the regulatory perimeter.
"""

ZODIA_REVERSE_SOLICITATION_FRAMEWORK = """
REVERSE SOLICITATION ANALYSIS FRAMEWORK:

For each jurisdiction, determine:

A. IS REVERSE SOLICITATION RECOGNIZED?
   - Is there an explicit reverse solicitation exemption in statute or regulation?
   - Is it only in regulatory guidance or practice (softer, can change)?
   - Or is reverse solicitation NOT recognized at all (all foreign providers caught)?

B. CONDITIONS FOR REVERSE SOLICITATION TO APPLY:
   - Must the client be the SOLE initiator of the relationship?
   - Is there a cooling-off or documentation requirement?
   - Does Zodia need to document/evidence that the client approached first?
   - Can Zodia provide ADDITIONAL services after the initial reverse solicitation, 
     or does each new service require fresh reverse solicitation?
   - Time limits: does the exemption expire (e.g., one-off transaction only)?

C. WHAT BREAKS REVERSE SOLICITATION:
   - Any marketing or advertising targeting the jurisdiction
   - Having a local-language website or local social media presence
   - Attending local conferences/events for marketing
   - Using local agents or introducers
   - Having any form of local operational presence
   - Proactively contacting the client about new products/services

D. PRACTICAL RISK ASSESSMENT:
   - How aggressively does the local regulator enforce against foreign VASPs?
   - Are there precedents of enforcement against foreign platforms relying on 
     reverse solicitation?
   - What are the penalties if the regulator determines reverse solicitation 
     conditions were NOT met?
   - Is there regulatory guidance that specifically addresses crypto/VASP 
     reverse solicitation (vs traditional finance reverse solicitation)?
"""
