# Commercial Switch v0.7.0 – specification

Production remains **pre-commercial** until the GO/NO-GO gate is PASS. No dormant commercial markup is shipped in production.

## Atomic web switch
- Homepage H1: direct service proposition only after GO.
- Replace all „služby pripravujem / komerčné služby zatiaľ neposkytujem“ wording with truthful live-service wording.
- `/revizie/`: actual scope, audience, service area, price path and contact route.
- CTA: contextual service CTA; sticky variant only on commercial customer-path pages after usability testing.
- Business identity/contact details: publish only finalized real data.
- Schema: activate only types supported by the actual business model. `ProfessionalService` is not used.
- Analytics: keep consent-first; add only `service_cta_click` and finalized contact-intent events. Raw search query remains redacted.

## Full-state commercial dry-run
The local builder creates a complete **non-production simulation** of the future commercial state, not only a CTA experiment. It transforms commercial-status copy across all HTML pages, makes unresolved GO/NO-GO inputs visibly explicit, and tests the customer-path CTA on the homepage and `/revizie/`. The inline CTA becomes a compact sticky bar after it scrolls out of view and hides again near the footer.

Acceptance rules:
- every dry-run HTML page is `noindex,nofollow` and visibly marked `DRY RUN – NEPUBLIKOVAŤ`;
- customer-path pages render service scope, service area, pricing, contact path, business identity, capacity and insurance decision placeholders instead of inventing data;
- the schema candidate is stored as non-JSON-LD `application/json` until provider/type/area/pricing decisions are truthful;
- no pre-commercial status wording may remain in the dry-run output;
- `.build/` remains outside the GitHub Pages publication surface; `noindex` is defense-in-depth, not the publication boundary;
- the full-state dry-run must never ship in the pre-commercial production build;
- rebuild the Search index from the transformed dry-run HTML so internal Search reflects the simulated commercial state;
- transform the dry-run `llms.txt` orientation copy so it does not contradict the simulated commercial state;
- expose `channel: local-dry-run` and `commercialState: commercial-simulation` in the dry-run `version.json`, while preserving the source release identity in the dry-run manifest;
- before the real v0.7.0 switch, regenerate Search, update `llms.txt`, switch `version.json`/commercial state and scan the whole public surface — not only HTML — for pre-commercial status wording;
- verify sitemap and metadata after the real state change.

## Schema decision matrix
- `Person`: keep author identity.
- `Project`: keep while the public site remains pre-commercial; reassess at GO.
- `Organization`: use only if the real commercial entity/brand model supports it.
- `Electrician`: use only if the operating business is truthfully represented by that LocalBusiness subtype and the required public data exist.
- `Service`: only for actually available services with a real provider.
- `Offer`: only for an actual, truthful offer/pricing model.
- Do not publish a home address merely to satisfy schema/rich-result expectations.

## Unresolved inputs
Business/legal setup, final service scope, service area, pricing model, commercial contact path, operating capacity and insurance applicability remain GO/NO-GO inputs; do not invent them in code or copy.
