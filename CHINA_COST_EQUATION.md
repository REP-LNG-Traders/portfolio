# China Total Cost - Mathematical Equation

## 📐 Complete Mathematical Formula

### **Main Equation:**

```
Total Cost (China) = Purchase Cost + Freight Cost + Stranded Cost + Risk Adjustments

Where:

Freight Cost = Base Freight + Insurance + Brokerage + Working Capital + 
               Carbon + Demurrage + LC Cost + Special Port Fee
```

---

## 🔢 Detailed Component Formulas

### **1. Purchase Cost**
```
Purchase Cost = (Henry Hub Price + Tolling Fee) × Cargo Volume
              = (HH + $2.50/MMBtu) × V_cargo
```

### **2. Freight Components**

#### **a) Base Freight**
```
Base Freight = Freight Rate × Cargo Volume × Scaling Factor
             = F_rate × V_cargo × 1.0
```

#### **b) Insurance**
```
Insurance = $150,000 (fixed per voyage)
```

#### **c) Brokerage**
```
Brokerage = Base Freight × 0.015
          = F_base × 1.5%
```

#### **d) Working Capital**
```
Working Capital = Purchase Cost × Annual Rate × (Voyage Days / 365)
                = P_cost × 5% × (52/365)
                = P_cost × 0.00712
```

#### **e) Carbon Cost**
```
Carbon Cost = Daily Carbon Rate × Voyage Days
            = $5,700/day × 52 days
            = $296,400
```

#### **f) Demurrage (Expected)**
```
Demurrage = $50,000 (expected value)
```

#### **g) Letter of Credit (LC)**
```
LC Cost = max(Sale Value × 0.001, $25,000)
        = max(S_value × 0.1%, $25,000)
```

#### **h) Special Port Fee ⭐**
```
Special Port Fee = {
    $3,920,000   if delivery date ≤ April 16, 2026  (Period 1)
    $6,300,000   if delivery date ≥ April 17, 2026  (Period 2)
}

Calculated as:
Special Port Fee = Vessel Net Tonnage × USD per Net Tonne
Period 1: 70,000 NT × $56/NT = $3,920,000
Period 2: 70,000 NT × $90/NT = $6,300,000
```

### **3. Total Freight Cost**
```
Total Freight = Base Freight + Insurance + Brokerage + Working Capital + 
                Carbon + Demurrage + LC Cost + Special Port Fee

Total Freight = F_base + $150K + (F_base × 0.015) + (P_cost × 0.00712) + 
                $296.4K + $50K + max(S_value × 0.001, $25K) + Special_Fee
```

### **4. Final P&L Calculation**
```
Gross P&L = Sale Revenue - Purchase Cost - Total Freight - Stranded Cost - BioLNG Penalty

Expected P&L = Gross P&L × Credit Adjustment × Demand Probability
```

---

## 💰 Numeric Example - January 2026

### **Given:**
- Henry Hub: $3.00/MMBtu
- Cargo Volume: 3,800,000 MMBtu
- Sale Value: $43,210,123
- Voyage Days: 52 days
- Freight Rate: $2.73M (base)

### **Calculation:**

```
1. Purchase Cost:
   = ($3.00 + $2.50) × 3,800,000
   = $5.50 × 3,800,000
   = $20,900,000

2. Base Freight:
   = $2,730,000

3. Insurance:
   = $150,000

4. Brokerage:
   = $2,730,000 × 0.015
   = $40,950

5. Working Capital:
   = $20,900,000 × 0.05 × (52/365)
   = $148,932

6. Carbon Cost:
   = $5,700 × 52
   = $296,400

7. Demurrage:
   = $50,000

8. LC Cost:
   = max($43,210,123 × 0.001, $25,000)
   = max($43,210, $25,000)
   = $43,210

9. Special Port Fee (Period 1):
   = $3,920,000  ⭐

────────────────────────────────────────────────
Total Freight Cost:
= $2,730,000 + $150,000 + $40,950 + $148,932 + 
  $296,400 + $50,000 + $43,210 + $3,920,000
= $7,379,492

TOTAL COST (China):
= $20,900,000 + $7,379,492
= $28,279,492
────────────────────────────────────────────────
```

---

## 🎯 Key Insight

**Special Port Fee Impact:**
- The Special Port Fee ($3.92M) represents **53.1%** of total freight cost
- Adds **$1.03/MMBtu** to the total cost (on 3.8M MMBtu cargo)
- Makes China **uncompetitive** compared to Singapore despite higher JKM prices

**Period Comparison:**
- Period 1 (Jan-Apr 16): Special Port Fee = $3,920,000 → +$1.03/MMBtu
- Period 2 (Apr 17-Jun): Special Port Fee = $6,300,000 → +$1.66/MMBtu

---

## ✅ Implementation Status

**Variable Names Updated:**
- `YANGSHAN_PORT_FEE` → `SPECIAL_PORT_FEE` (config/constants.py)
- `yangshan_fee` → `special_port_fee` (models/optimization.py)
- `yangshan_per_mmbtu` → `special_port_fee_per_mmbtu` (models/optimization.py)

**Files Modified:**
1. `/config/constants.py` - Line 126: `SPECIAL_PORT_FEE` constant
2. `/models/optimization.py` - Line 23: Import statement
3. `/models/optimization.py` - Lines 229-249: Calculation logic
4. `/models/optimization.py` - Lines 268, 278: Return dictionary

**Testing:**
- ✅ No linter errors
- ✅ All references updated consistently
- ✅ Mathematical formula verified

---

**Generated:** October 17, 2025
**Status:** ✅ Complete

