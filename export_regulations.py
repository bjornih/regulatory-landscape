#!/usr/bin/env python3
"""
Export client-relevant regulations from Airtable to a static JSON file.

Usage:
    python export_regulations.py

Requires the AIRTABLE_TOKEN environment variable to be set with a valid
Airtable Personal Access Token that has read access to the Regulation Tracker base.

The script:
  1. Fetches all records from the Legislative Tracker table
  2. Resolves Airtable select/multiselect objects to plain strings
  3. Filters out records marked as "Internal Only" (audience field)
  4. Excludes the internal-only fields (Audience, Internal Compliance Notes)
  5. Writes the result to regulations.json
"""

import json
import os
import sys
import urllib.request
import urllib.error

# ── Configuration ──

AIRTABLE_BASE_ID = "appeYbPlhADVJHQYN"
AIRTABLE_TABLE_ID = "tblOxo7T1GbetZHUr"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regulations.json")

# Field IDs to fetch (everything except Internal Compliance Notes)
FIELD_IDS = {
    "fldVgexH23DpuzHzY": "Legislation",
    "fldtmymnaBpBAkQel": "Full Name",
    "fldqWjQHJpZ2QbbkO": "Categories",
    "fld9BjWNDxKLzPZ5O": "Jurisdiction",
    "fldpmpAVryDnSHkW5": "Status",
    "fld3ZnqdANNp7QKK9": "Relevance",
    "flde16q1AixwEWkQ5": "Domains",
    "fldRWCa3e2UJ8rYFZ": "Brief Description",
    "fldD3mgpdDyNOsXA2": "Type",
    "fldHj2q0UwMAjuyBF": "Enacted",
    "fldwpQ91u8T8YITvb": "In Force",
    "fldlMkbHRiGC7kaKa": "Deadline",
    "fldrFQ4lCQD4pyght": "Next Steps",
    "fldIXRxgEnHwKFjsg": "Scope",
    "fldNLJ1KpDQF96L2l": "Enforcement",
    "fldLJe9RJyWqcNHVy": "Relevance Notes",
    "fldBYPbuoLTHG78TD": "Source",
    "fldIFXKD4YZda3WuS": "Audience",  # Used for filtering, not included in output
    "fldmJYAT2NgT99MEI": "Last Modified",
    "fldp1hAp1YivxMNKo": "Policy Requirements",  # Linked records to Policy Requirements table
    "fld0ZoUSwQkCiBAsr": "Regulatory Definitions",  # Linked records to Regulatory Definitions table
}

AUDIENCE_FIELD_ID = "fldIFXKD4YZda3WuS"

# Linked record fields: exported as counts rather than raw record IDs
LINKED_RECORD_COUNT_FIELDS = {
    "Policy Requirements": "Obligation Count",
    "Regulatory Definitions": "Definition Count",
}


def resolve_value(val):
    """Resolve Airtable select/multiselect objects to plain strings."""
    if val is None:
        return val
    if isinstance(val, dict) and "name" in val:
        return val["name"]
    if isinstance(val, list):
        return [v["name"] if isinstance(v, dict) and "name" in v else v for v in val]
    return val


def fetch_all_records(token: str) -> list[dict]:
    """Fetch all records from Airtable with pagination."""
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    all_records = []
    offset = None

    while True:
        url = f"{base_url}?pageSize=100"
        if offset:
            url += f"&offset={offset}"

        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"Airtable API error: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)

        all_records.extend(data.get("records", []))
        offset = data.get("offset")

        if not offset:
            break

    return all_records


def transform_record(record: dict) -> dict | None:
    """
    Transform an Airtable record into a clean dict for the website.
    Returns None if the record should be excluded (Internal Only).
    """
    fields = record.get("fields", {})

    # Check audience -- skip Internal Only records
    audience = resolve_value(fields.get("Audience"))
    if audience == "Internal Only":
        return None

    # Build clean record with friendly field names
    entry = {}
    for field_id, field_name in FIELD_IDS.items():
        if field_name == "Audience":
            continue  # Don't include audience in public output

        # Linked record fields: export as counts with a friendly key name
        if field_name in LINKED_RECORD_COUNT_FIELDS:
            raw = fields.get(field_name)
            if isinstance(raw, list) and len(raw) > 0:
                entry[LINKED_RECORD_COUNT_FIELDS[field_name]] = len(raw)
            continue

        raw = fields.get(field_name)
        resolved = resolve_value(raw)

        if resolved is not None and resolved != "" and resolved != []:
            entry[field_name] = resolved

    return entry


def main():
    token = os.environ.get("AIRTABLE_TOKEN")
    if not token:
        print("Error: AIRTABLE_TOKEN environment variable is not set.", file=sys.stderr)
        print("Set it with: export AIRTABLE_TOKEN='pat...'", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching records from Airtable...")
    raw_records = fetch_all_records(token)
    print(f"  Fetched {len(raw_records)} total records")

    # Transform and filter
    records = []
    skipped = 0
    for raw in raw_records:
        entry = transform_record(raw)
        if entry is not None:
            records.append({"fields": entry})
        else:
            skipped += 1

    print(f"  Client-visible: {len(records)} records")
    if skipped:
        print(f"  Excluded (Internal Only): {skipped} records")

    # Write output
    output = {"records": records}
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"  Written to: {OUTPUT_FILE} ({file_size:,} bytes)")


if __name__ == "__main__":
    main()
