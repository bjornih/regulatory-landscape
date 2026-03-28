# Regulatory Landscape

An interactive reference tool mapping regulations and standards across jurisdictions that are relevant to cross-domain threat intelligence. Built and maintained by [Revontulet AS](https://revontulet.co) (Org. Nr. 933 793 133).

## Purpose

This resource is designed to help organizations understand the regulatory environment affecting cross-domain threat intelligence work. It provides a searchable, filterable overview of legislation, frameworks, and standards across multiple jurisdictions, covering domains such as cybersecurity, AML/CFT, content governance, data protection, AI regulation, and more.

It is not a compliance tool. It is an informational starting point for understanding what exists and where obligations may arise.

## Live versions

- GitHub Pages: https://bjornih.github.io/regulatory-landscape/
- Public website: https://revontulet.co/regulatory-landscape

## Data pipeline

Regulatory data is managed in Airtable and exported to this repository via a scheduled GitHub Action.

1. **Airtable** holds the source data (legislation records, policy requirements, regulatory definitions)
2. **`export_regulations.py`** fetches records from Airtable, filters out internal-only entries, and writes `regulations.json`
3. **GitHub Actions** runs the export weekly (Mondays 06:00 UTC) and on manual trigger, committing any changes to `regulations.json`
4. **`index.html`** is a single-file static site that loads `regulations.json` at runtime and renders the card grid, filters, and search

The `index.html` references `regulations.json` via an absolute GitHub raw URL, so the same file can be embedded in external sites (e.g. Squarespace) while pulling live data from this repository.

## Reporting issues

If you spot an error in the data, a missing regulation, or a broken feature, please [open an issue](https://github.com/bjornih/regulatory-landscape/issues) on this repository.

## Copyright

Copyright 2024-2026 Revontulet AS. All rights reserved.

This repository and all of its contents, including but not limited to code, data, text, and design, are the intellectual property of Revontulet AS. No part of this repository may be reproduced, distributed, modified, or used for commercial purposes without prior written permission from Revontulet AS.

Viewing this repository on GitHub does not grant any license to use, copy, or distribute its contents beyond what is necessary to view the publicly hosted versions linked above.

## Disclaimer

This resource is developed for informational purposes only and does not constitute legal advice. The information presented may not be complete, current, or applicable to any specific situation. Organizations should consult qualified legal counsel regarding their specific compliance obligations.
