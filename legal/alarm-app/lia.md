# Legitimate Interest Assessment (LIA)

**Controller:** Smart Horizon
**Application:** OkiSpark, alarm mobile application (no user accounts)  
**Date:** 2026-11-20 (previous: 2026-01-24)  
**Review Cycle:** Upon material change to data processing

---

## 1. Purpose Test

### What is the legitimate interest?

The legitimate interest pursued is to ensure the reliability, stability, security, and continuous improvement of the mobile application.

Analytics, diagnostic and performance data (Firebase Analytics, Crashlytics and Performance Monitoring) and subscription events reported by RevenueCat are processed to:
- Detect and fix crashes and technical errors
- Monitor application performance and stability, including whether alarms appear on time
- Identify feature malfunctions
- Improve user experience based on aggregated usage patterns
- Understand subscription conversion and revenue

These purposes are necessary for operating and maintaining a functional mobile application and align with reasonable user expectations.

**GDPR Reference:**  
Article 6(1)(f) — Lawfulness of processing  
https://gdpr-info.eu/art-6-gdpr/

---

## 2. Necessity Test

### Is the processing necessary?

Yes.

The stated purposes cannot be reasonably achieved without collecting limited analytics and diagnostic data, such as:
- Application version, device type and operating system version
- Feature events and screen names, without free text (no alarm labels, typed text, photos, barcode values, locations or health values)
- General properties: app language, Pro status, number of alarms as a range, theme and clock format
- Crash reports, error reports and performance timings
- Subscription events with price and currency (via RevenueCat)
- Country or region derived by Google from the IP address only

No alternative method would provide equivalent insight into application stability and performance without processing such data.

The processing is proportionate and limited to what is strictly necessary.

**GDPR Reference:**  
Recital 39 — Data minimisation  
https://gdpr-info.eu/recitals/no-39/

---

## 3. Balancing Test

### Does the processing override user rights?

The impact on user privacy is assessed as low, based on the following factors:

#### Nature of the data
- No names, email addresses, or account identifiers; only a random app-installation identifier
- No precise location data (approximate location is used only for weather and is never sent to analytics)
- No health data (Apple Health / Health Connect data stays on the device)
- No profiling or behavioral advertising
- No combination with third-party identity data

#### Reasonable expectations
Users reasonably expect a mobile application to:
- Monitor crashes
- Improve performance
- Fix bugs

This processing is common industry practice and does not result in unexpected or intrusive outcomes.

**GDPR Reference:**  
Recital 47 — Reasonable expectations  
https://gdpr-info.eu/recitals/no-47/

---

## 4. Safeguards and Mitigations

The following safeguards are implemented:
- Data minimization (only essential analytics collected)
- Pseudonymization and aggregation
- Limited data retention (Crashlytics about 90 days; Analytics events no longer than 14 months)
- Transparency via the Privacy Policy
- User right to object through an in-app switch (Settings → Privacy & terms → "Share anonymous usage data"): turning it off immediately stops analytics, crash reporting and performance monitoring, deletes unsent crash reports, resets the analytics identifier, and stops RevenueCat linking purchases to Analytics; restoring a backup never re-enables it
- Nothing is sent from development builds
- No sale or sharing of data for advertising purposes

**GDPR References:**  
Article 5(1)(c) — Data minimisation  
https://gdpr-info.eu/art-5-gdpr/  
Article 21 — Right to object  
https://gdpr-info.eu/art-21-gdpr/

---

## 5. Conclusion

After assessing the purpose, necessity, balancing of interests, and safeguards in place, it is concluded that the processing of limited analytics and diagnostic data under Legitimate Interest (Article 6(1)(f)) does not override the rights and freedoms of users.

The processing is lawful, proportionate, and defensible.

---

## 6. Review

This assessment will be reviewed if:
- New categories of data are introduced (reviewed 2026-11-20 for Crashlytics, Performance Monitoring, RevenueCat purchase events and the in-app switch)
- Analytics providers or purposes change
- Applicable regulatory guidance materially changes
