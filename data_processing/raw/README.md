# Raw Data Directory

## 📥 Place Your Excel Files Here

This directory should contain the following files:

### Required Files:

1. **`lng_prices_asia.xlsx`**
   - Historical LNG prices for Asian markets
   - Columns: Date, Market, Price
   - Markets: Singapore, China, Japan
   - Frequency: Monthly data
   - Minimum 24 months of history recommended

2. **`production_cost.xlsx`**
   - LNG production costs over time
   - Columns: Date, Cost_per_MMBtu

3. **`freight_cost.xlsx`**
   - Freight costs by route and market
   - Columns: Route, Market, Cost_per_MMBtu

---

## 🧪 Testing Without Real Data

If you don't have real data yet, generate sample data for testing:

```bash
python generate_sample_data.py
```

This will create synthetic Excel files in this directory with realistic LNG market characteristics.

---

## ⚠️ Important Notes

- **File names must match** those specified in `config.py` → `DATA_FILES`
- **Column names** can vary - configure mappings in `config.py` → `COLUMN_MAPPING`
- **Market names** can vary - configure mappings in `config.py` → `MARKET_MAPPING`
- Ensure dates are in a consistent format (YYYY-MM-DD recommended)
- Remove any header rows or summary statistics from Excel files

---

## 📋 Example Data Format

### lng_prices_asia.xlsx
```
Date       | Market    | Price
-----------|-----------|-------
2022-01-01 | Singapore | 15.20
2022-01-01 | China     | 16.50
2022-01-01 | Japan     | 17.10
2022-02-01 | Singapore | 14.80
2022-02-01 | China     | 16.20
2022-02-01 | Japan     | 16.90
...
```

### production_cost.xlsx
```
Date       | Cost_per_MMBtu
-----------|---------------
2022-01-01 | 4.50
2022-02-01 | 4.55
2022-03-01 | 4.60
...
```

### freight_cost.xlsx
```
Route | Market    | Cost_per_MMBtu
------|-----------|---------------
R1    | Singapore | 1.20
R2    | China     | 1.50
R3    | Japan     | 1.30
```

---

**Ready to proceed once files are in place!** ✅



