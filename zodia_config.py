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
    "summary": "Concise overview of the country's regulatory regime as it applies to Zodia Markets' specific business: institutional OTC brokerage, electronic spot trading, fiat-to-crypto conversion, and non-custodial digital asset services",
    "high_level_risk_points": "Key regulatory risks for Zodia Markets specifically - focus on risks to its OTC brokerage, exchange, fiat-on-ramp, cross-border services, and non-custodial model",
    "regulatory_framework": "The regulatory framework that governs Zodia's activities: which laws/regulations cover (a) OTC crypto brokerage, (b) electronic trading platforms for digital assets, (c) fiat-to-crypto conversion, (d) crypto-to-crypto exchange, (e) non-custodial models with delegated custody",
    "virtual_asset_trading_platforms": "Specific licensing/authorization requirements for operating an electronic trading platform or exchange for digital assets in this jurisdiction, including market operator licenses, MTF/OTF rules if applicable",
    "stablecoin_regulation": "Rules specifically affecting stablecoin trading, settlement, and fiat-backed token transactions - relevant because Zodia trades USDC, USDT, EURC and offers stablecoin payment services",
    "store_of_value_facility_rules": "Regulations on store of value facilities, e-money, and payment token rules that apply to stablecoin trading and settlement models",
    "regulatory_expectations_and_licensing_triggers": "What specific activities trigger a licensing requirement in this jurisdiction? Map each of Zodia's activities (OTC brokerage, exchange, fiat gateway, custody delegation) to the specific license/authorization needed",
    "reverse_solicitation_and_direct_market_access": "CRITICAL: (a) Does this jurisdiction allow REVERSE SOLICITATION - can a local institutional client approach Zodia (a foreign VASP) on their own initiative and use Zodia's services without Zodia needing a local license? What are the conditions and limitations? (b) Is DIRECT MARKET ACCESS allowed - can Zodia provide its trading platform directly to clients in this jurisdiction from its UK/Ireland/ADGM/Jersey entities without establishing local presence? (c) What marketing/solicitation restrictions exist?",
    "cross_border_client_advisory": "Can Zodia Markets legally serve an institutional client from this jurisdiction? Analyze: (a) Does this country require foreign VASPs to hold a local license before serving local institutional clients? (b) Which Zodia entity (UK, Ireland, ADGM, Jersey) is best positioned to serve this client? (c) Can Zodia rely on EU/MiCA passporting from Ireland if applicable? (d) What AML/KYC obligations does the local jurisdiction impose?",
    "compliance_guidance_and_recommendations": "Actionable compliance advice: (a) Clear verdict: SERVE / SERVE WITH CONDITIONS / DECLINE with reasoning (b) What steps must Zodia take before onboarding? (c) Which Zodia entity should service the relationship? (d) What enhanced due diligence or restrictions apply? (e) If a local license is needed, what type and process?"
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
