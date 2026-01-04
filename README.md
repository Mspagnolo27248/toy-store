# 🧸 Toy Shop Simulator — Quick, focused README

One-line summary

An interactive Streamlit game: produce toys, set prices, and manage
inventory across several days to maximize cash + inventory value.

Quick start

```bash
python3 -m venv .venv        # optional
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Core model (short)

- Demand: `max(0, Base Demand + Coefficient × Price)` (Coefficient is
   usually negative).
- Scenarios: daily multipliers (holiday, recession, marketing, etc.)
   adjust price sensitivity.
- Costs: daily production cost is drawn from `[min_cost, max_cost]`.
- Inventory & COGS: unsold units remain; COGS uses weighted average
   production cost when items are sold.

Report — what to look for

- `Revenue` = units sold × price
- `Costs/COGS` = units sold × avg production cost
- `Profit (round)` = revenue − COGS
- `Inventory Value` = remaining units × avg cost (cost-basis)
- `Total Value` = cumulative profit + inventory cost

Quick tips

- Watch average inventory cost before producing large batches.
- Raise production when a positive scenario appears only if cash allows.
- Test price changes: lower price → more units, lower margin per unit.

Files

- `streamlit_app.py`: app and simulation logic
- `requirements.txt`: dependencies

License

See the repository `LICENSE` file.
