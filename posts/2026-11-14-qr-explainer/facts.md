# Facts — "QR भुक्तानी: भित्र के हुन्छ?" (भित्र के हुन्छ? series, भाग १)
Prepared 2026-11-14. Every figure/step below is tied to a source. Illustrative examples are marked.

## Process (Level 1 — NRB framework)
Source A: Nepal Rastra Bank, Payment Systems Department, "NepalQR Standardization Framework and Guidelines" + "QR Code Specifications" (February 2021).
https://www.nrb.org.np/contents/uploads/2021/01/QR-Code-Guidelines-and-Framework-and-Specifications.pdf

1. Standard: based on EMVCo standard v4.3; "Merchant Presented" QR (customer scans the merchant's QR).
2. QR content (Spec Table 1): network-specific merchant identifier tags, Merchant Category Code (tag 52), optional Transaction Amount (tag 54), Merchant Name (tag 59), Merchant City (tag 60). Point-of-initiation "11" = static, "12" = dynamic.
3. Issuer = network member that manages customers and enables payments from bank/savings/e-money/card accounts. "The Issuer application shall scan the QR, parse all the parameters of the QR" (4.6).
4. Acquirer = BFI or licensed PSP "responsible for enrolling merchants, assigning merchant IDs, maintaining merchant records/accounts and settling merchants".
5. Network/scheme operator = licensed PSO that routes transactions among members; "Scheme/Network shall settle the transaction and provide the transaction reports" (4.4).
6. Merchant notification (4.5.12): confirmed status Success/Failed; payment-credit status; "SMS/notification for every transaction".
7. Settlement (4.8): network calculates each member's net debit/credit position from acquiring+issuing; net-debit members keep funds in settlement accounts; at end of each cutover a daily settlement report is prepared. Annex II diagram note: network "debits the issuers and credits the acquirers"; acquirer "reconciles and credits the merchant account post service fee deductions".
   - NOT stated in source: exact cut-off time, T+0, RTGS. → Video says only "पछि, तोकिएको चक्रमा / दिनभरको हिसाब". Do not claim when the merchant's account balance is credited.

## Interoperability (Level 1 — NCHL)
Source B: NCHL, NEPALPAY QR page (accessed 2026-11-14) https://nchl.com.np/nepalpay-qr/ and connectIPS "Know more" https://connectips.com/knowmore/nepalpayqr/
- NEPALPAY QR = national QR scheme implemented by NCHL "as the implementing infrastructure of NepalQR standards"; allows interoperability "at merchant level and network level".
- Page lists 56 Scan & Pay sources (banks, finance companies, wallets, connectIPS app) and 52 acquirers (counted from page lists, 2026-11-14).
- Payer steps: log in to mobile banking/wallet/connectIPS → Scan to pay → enter amount (auto for dynamic QR) → confirm with transaction password and/or OTP.
- Fonepay is a separate QR network (named as an example only; no Fonepay figures used).

## Scale (Level 1 — NRB statistics)
Source C: NRB, Payment Systems Indicators, Bhadra 2083 (mid-Aug to mid-Sep 2026) https://www.nrb.org.np/contents/uploads/2026/10/PS-Bhadra-2083_.pdf
- QR-Based Payments, number: 75,581,982 (Bhadra 2082: 41,087,808) → +83.9% ≈ +84%
- QR-Based Payments, amount: NPR 167,933 million = रु. १ खर्ब ६७ अर्ब ९३ करोड ≈ रु. १.६८ खर्ब (Bhadra 2082: NPR 101,239 million) → +65.9% ≈ +66%
- Arithmetic checked in Python (see build log).

## Illustrative only (labelled "उदाहरण" on screen)
- "राम चिया पसल", रु. ५००, Bank A/B netting रु. १,००० vs रु. ७०० → खुद रु. ३००. Fictional.

## Safety line
- Scanning a merchant QR sends money from you ("तिर्नुहुन्छ, पाउनुहुन्न") — follows from merchant-presented flow (Source A). NRB has separately warned about fake QR/accounts (Dashain 2026 alert, ShareSansar 2026-10-20).

## Opinion
- None in this episode beyond the safety reminder.
