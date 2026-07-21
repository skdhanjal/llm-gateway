import json, csv, io
import yaml   # pip install pyyaml
from gateway.token_math import count_tokens
from gateway.config import MODEL_PRICES, settings

# --- synthetic but realistic records (order-line style) ---
RECORDS = [
    {"order_id": 10000 + i, "customer_name": f"Customer {i}",
     "product_sku": f"SKU-{i%7:03d}", "quantity": (i % 5) + 1,
     "unit_price_inr": 499.0 + i, "status": ["shipped","pending","delivered"][i % 3]}
    for i in range(40)
]

def as_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
    return buf.getvalue()

def as_md_table(rows):
    keys = list(rows[0].keys())
    lines = ["| " + " | ".join(keys) + " |",
             "|" + "---|" * len(keys)]
    lines += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in rows]
    return "\n".join(lines)

FORMATS = {
    "json_pretty": json.dumps(RECORDS, indent=2),
    "yaml":        yaml.dump(RECORDS, sort_keys=False),
    "json_min":    json.dumps(RECORDS, separators=(",", ":")),
    "md_table":    as_md_table(RECORDS),
    "csv":         as_csv(RECORDS)
}

model = settings.default_model
p_in = MODEL_PRICES[model]["input"]
base = None

print(f"{'format':12s} {'tokens':>7s} {'vs json_pretty':>14s} {'$/1M requests':>14s}")

for name, payload in FORMATS.items():
    t = count_tokens(payload, model)
    base = base or t
    cost_1m = t * p_in / 1_000_000 * 1_000_000   # $ per 1M requests, input side
    print(f"{name:12s} {t:7d} {t/base*100:13.1f}% {cost_1m:14,.0f}")