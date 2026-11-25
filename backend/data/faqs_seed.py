from typing import List, Dict, Any

SEED_FAQS: List[Dict[str, Any]] = [
    # 1. Account
    {
        "id": "FAQ-ACC-01",
        "category": "Account",
        "question": "How can I update my profile details?",
        "answer": "Log in to your TechNova account, navigate to Account Settings -> Profile, edit your details (such as name, phone number, or display preferences), and click 'Save Changes'.",
        "keywords": ["profile", "update", "details", "name", "email change", "settings"]
    },
    {
        "id": "FAQ-ACC-02",
        "category": "Account",
        "question": "How do I delete or deactivate my account?",
        "answer": "To permanently delete or deactivate your account, go to Account Settings -> Privacy & Data -> Delete Account. Please note this action is irreversible and will erase your saved preferences and order history.",
        "keywords": ["delete", "deactivate", "close account", "erase data", "remove account"]
    },
    {
        "id": "FAQ-ACC-03",
        "category": "Account",
        "question": "Can I transfer my account ownership to another email?",
        "answer": "Yes, you can update your primary account email by going to Account Settings -> Security -> Primary Email, entering the new email address, and verifying it via the confirmation link sent to the new inbox.",
        "keywords": ["transfer", "ownership", "change email", "primary email", "new account email"]
    },

    # 2. Password
    {
        "id": "FAQ-PWD-01",
        "category": "Password",
        "question": "How can I reset my password?",
        "answer": "Go to the TechNova login page and select 'Forgot Password'. Enter your registered email address and follow the password-reset link sent to your inbox.",
        "keywords": ["password", "reset", "forgot password", "login issue", "change password"]
    },
    {
        "id": "FAQ-PWD-02",
        "category": "Password",
        "question": "What are the password requirements for TechNova?",
        "answer": "TechNova passwords must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (e.g. @, #, $).",
        "keywords": ["password requirements", "strong password", "character limit", "rules", "password complexity"]
    },

    # 3. Security
    {
        "id": "FAQ-SEC-01",
        "category": "Security",
        "question": "How do I enable Two-Factor Authentication (2FA)?",
        "answer": "Open Account Settings -> Security -> Two-Factor Authentication. Scan the provided QR code using Google Authenticator, Authy, or Duo, then enter the 6-digit confirmation code.",
        "keywords": ["2fa", "two-factor", "security", "authenticator", "mfa", "otp", "login code"]
    },
    {
        "id": "FAQ-SEC-02",
        "category": "Security",
        "question": "What should I do if I suspect an unauthorized login?",
        "answer": "If you notice unrecognized activity, go to Account Settings -> Active Sessions and click 'Log Out All Devices'. Immediately reset your password and verify your 2FA settings.",
        "keywords": ["unauthorized", "hacked", "suspicious activity", "logout devices", "security breach"]
    },

    # 4. Billing
    {
        "id": "FAQ-BIL-01",
        "category": "Billing",
        "question": "Where can I view and download my invoices?",
        "answer": "Navigate to Account Settings -> Billing & Invoices. You will see a chronological list of past transactions with buttons to download PDF invoices.",
        "keywords": ["invoice", "receipt", "billing history", "download PDF", "tax receipt"]
    },
    {
        "id": "FAQ-BIL-02",
        "category": "Billing",
        "question": "Why was I charged twice for the same billing cycle?",
        "answer": "Duplicate charges can occur if a transaction attempt timed out while processing. Any authorization holds automatically clear within 3-5 business days. If both charges post, please contact our billing team with your transaction IDs.",
        "keywords": ["charged twice", "double charge", "duplicate charge", "pending authorization", "overcharge"]
    },
    {
        "id": "FAQ-BIL-03",
        "category": "Billing",
        "question": "Can I get a tax-exempt status for my company invoice?",
        "answer": "Yes. Business accounts can submit their VAT / GST / Tax ID under Billing Settings -> Business Information to apply tax exemption to future billing statements.",
        "keywords": ["tax exempt", "vat", "gst", "business invoice", "tax id"]
    },

    # 5. Payments
    {
        "id": "FAQ-PAY-01",
        "category": "Payments",
        "question": "What payment methods are supported?",
        "answer": "Customers can pay using supported credit cards (Visa, MasterCard, American Express), debit cards, UPI, Apple Pay, Google Pay, and PayPal.",
        "keywords": ["payment methods", "credit card", "debit card", "upi", "paypal", "apple pay"]
    },
    {
        "id": "FAQ-PAY-02",
        "category": "Payments",
        "question": "Why was my payment declined?",
        "answer": "Payments may be declined due to insufficient funds, incorrect CVV/expiry date, bank fraud blocks, or international card restrictions. We recommend verifying your card details or contacting your card issuer.",
        "keywords": ["payment declined", "declined", "card fail", "payment error", "transaction failed"]
    },
    {
        "id": "FAQ-PAY-03",
        "category": "Payments",
        "question": "Is my payment information secure on TechNova?",
        "answer": "Yes. All payments are encrypted using AES-256 and PCI-DSS Level 1 compliant gateways. TechNova never stores your full card credentials on our servers.",
        "keywords": ["payment security", "pci dss", "encryption", "card security", "safe payment"]
    },

    # 6. Subscription
    {
        "id": "FAQ-SUB-01",
        "category": "Subscription",
        "question": "How can I cancel my subscription?",
        "answer": "Open Account Settings -> Subscription -> Manage Subscription -> Cancel Subscription. You will retain full plan access until the end of your current billing period.",
        "keywords": ["cancel subscription", "cancel plan", "unsubscribe", "stop auto renew", "membership"]
    },
    {
        "id": "FAQ-SUB-02",
        "category": "Subscription",
        "question": "How do I upgrade or downgrade my plan?",
        "answer": "Go to Account Settings -> Subscription -> Change Plan. Select your desired plan (Starter, Professional, or Enterprise). Upgrades take effect immediately with pro-rated billing.",
        "keywords": ["upgrade plan", "downgrade plan", "change plan", "tier", "pro plan", "enterprise"]
    },
    {
        "id": "FAQ-SUB-03",
        "category": "Subscription",
        "question": "Is there a free trial for premium features?",
        "answer": "Yes, TechNova offers a 14-day free trial on the Professional Plan with no credit card required at sign-up.",
        "keywords": ["free trial", "trial period", "try pro", "14 day trial", "demo plan"]
    },

    # 7. Orders
    {
        "id": "FAQ-ORD-01",
        "category": "Orders",
        "question": "Where is my order and how can I track it?",
        "answer": "You can track your order by clicking 'My Orders' in your account menu or visiting the Order Tracking page with your Order Reference Number (e.g. ORD-9821). Tracking updates appear within 24 hours of shipment.",
        "keywords": ["track order", "order status", "where is my order", "order tracking", "shipment status"]
    },
    {
        "id": "FAQ-ORD-02",
        "category": "Orders",
        "question": "Can I modify or cancel my order after placing it?",
        "answer": "Orders can be modified or cancelled within 1 hour of placement from My Orders -> Cancel Order. Once an order enters processing/fulfillment, it cannot be modified.",
        "keywords": ["cancel order", "modify order", "change address order", "edit order"]
    },

    # 8. Shipping
    {
        "id": "FAQ-SHP-01",
        "category": "Shipping",
        "question": "What shipping options and delivery timelines are available?",
        "answer": "We offer Standard Shipping (3-5 business days), Express Shipping (1-2 business days), and International Shipping (7-14 business days depending on customs).",
        "keywords": ["shipping options", "delivery time", "express shipping", "standard delivery", "international shipping"]
    },
    {
        "id": "FAQ-SHP-02",
        "category": "Shipping",
        "question": "Do you ship internationally?",
        "answer": "Yes, TechNova ships to over 60 countries worldwide. Duties and taxes are calculated at checkout based on destination customs guidelines.",
        "keywords": ["international shipping", "worldwide delivery", "customs", "duties", "global shipping"]
    },

    # 9. Refunds
    {
        "id": "FAQ-RFD-01",
        "category": "Refunds",
        "question": "How long does a refund take?",
        "answer": "Approved refunds are generally processed within 5-7 business days to your original payment method, depending on your bank's processing timelines.",
        "keywords": ["refund time", "how long refund", "refund process", "return money", "payout"]
    },
    {
        "id": "FAQ-RFD-02",
        "category": "Refunds",
        "question": "What is TechNova's return and refund policy?",
        "answer": "We offer a 30-day money-back guarantee for software subscriptions and unused hardware products in original packaging. Requests after 30 days require special support authorization.",
        "keywords": ["refund policy", "return policy", "money back guarantee", "30 day return", "refund terms"]
    },
    {
        "id": "FAQ-RFD-03",
        "category": "Refunds",
        "question": "Can I get a refund for an unused partial month subscription?",
        "answer": "Subscription cancellations stop future renewals, but partial month refunds are not issued automatically unless requested within 48 hours of billing.",
        "keywords": ["partial refund", "unused subscription refund", "cancel refund", "prorated refund"]
    },

    # 10. Technical Support
    {
        "id": "FAQ-TEC-01",
        "category": "Technical Support",
        "question": "What should I do if the web app fails to load or shows a 500 error?",
        "answer": "Try clearing your browser cache and cookies, disabling ad-blockers, or switching to an incognito window. You can also verify service health at status.technova.com.",
        "keywords": ["500 error", "app crash", "not loading", "blank page", "cache clear", "status page"]
    },
    {
        "id": "FAQ-TEC-02",
        "category": "Technical Support",
        "question": "How do I generate an API key for integrations?",
        "answer": "Go to Account Settings -> Developer Tools -> API Keys, click 'Create New Key', assign permissions, and save the key string securely.",
        "keywords": ["api key", "developer key", "integration", "rest api", "token"]
    },
    {
        "id": "FAQ-TEC-03",
        "category": "Technical Support",
        "question": "Which web browsers are supported by TechNova?",
        "answer": "TechNova supports the latest versions of Google Chrome, Mozilla Firefox, Apple Safari, and Microsoft Edge.",
        "keywords": ["supported browsers", "chrome", "firefox", "safari", "edge", "compatibility"]
    },
    {
        "id": "FAQ-TEC-04",
        "category": "Technical Support",
        "question": "How do I troubleshoot mobile app sync issues?",
        "answer": "Ensure your mobile device has active internet, force-close the TechNova app, and re-open it. If issues persist, check app updates in App Store or Google Play Store.",
        "keywords": ["mobile app", "sync issue", "app sync", "ios android", "troubleshoot app"]
    }
]
