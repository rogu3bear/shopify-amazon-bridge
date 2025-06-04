# Agent Governance: Codex

## 1. Scope
Codex is limited to researching Amazon Seller Central docs, SP-API references, Shopify Admin API docs, official GS1 guidelines, and Wikipedia product-category pages only.

## 2. Allowed Domains
- sellercentral.amazon.com
- developer-docs.amazon.com
- *.myshopify.com
- shopify.dev
- gs1.org
- en.wikipedia.org

## 3. Disallowed
No personal data, no live price scraping, no login-required portals, no file downloads larger than 2 MB.

## 4. Rate Limits
Max 5 requests/min, 500 KB/response hard cap.

## 5. Mandatory Citations
Every factual claim or mapping table must embed source URL in a Markdown footnote.

## 6. Self-Validation Loop
Before emitting code, run internal checklist: schema match, field-length compliance, citation presence. Abort with error message if any check fails.

## 7. Command Syntax
All outbound requests via `requests.get()` wrapped by `cursor.net_request()`.

## 8. Security
No dynamic `exec`, no shell execution, no writing outside `catalog-sync/`.

## 9. Tagging Compliance
Include `[WORKSPACE:Development]` and `[PROJECT:Shopify-Amazon-Bridge]` headers in every generated multi-file output block.

## 10. Escalation
If rule conflict arises, halt and output "REQUIRES MANUAL REVIEW".

*(Placeholders such as API keys must never be committed.)* 