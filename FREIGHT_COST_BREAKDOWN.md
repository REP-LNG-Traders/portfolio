# Comprehensive Freight and Shipping Cost Components

## Overview
This document details all cost components included in the comprehensive freight cost calculation for LNG cargo shipping.

---

## Cost Components Summary

### 1. **Base Freight Cost**
- **Source**: Baltic LNG freight rate (BLNG 1)
- **Formula**: `Baltic Rate ($/day) × Voyage Days × Route Scaling Factor`
- **Route Scaling Factors**:
  - Singapore: 0.9 (shorter route, 10% discount)
  - Japan: 1.0 (baseline)
  - China: 1.05 (longer route, 5% premium)

### 2. **Insurance Costs**
- **Source**: [bplan.ai](https://bplan.ai/blogs/running-expenses/lng-liquefied-natural-gas-shipping-and-transportation-running-expenses)
- **Annual Premium**: $650,000 (mid-range estimate)
- **Per Voyage**: $54,167 (annual / 12 months)
- **Per MMBtu**: $0.016
- **Components**:
  - Hull & Machinery: 40%
  - Protection & Indemnity: 35%
  - War Risk: 15%
  - Cargo Insurance: 10%

### 3. **Brokerage Costs**
- **Source**: Industry standard maritime brokerage services
- **Rate**: 1.25% of base freight cost
- **Description**: Ship brokerage commission for arranging the charter

### 4. **Working Capital Costs**
- **Source**: Industry standard commodity trade finance rates 2024-2025
- **Rate**: 6% per annum (SOFR + spread)
- **Formula**: `Purchase Cost × 6% × (Voyage Days / 365)`
- **Description**: Interest cost on capital tied up during voyage period

### 5. **Carbon Costs (Destination-Specific)**
- **Sources**: 
  - [mdpi.com - EU Fit for 55](https://www.mdpi.com/2077-1312/10/7/946)
  - [waytronsc.com - IMO regulations](https://www.waytronsc.com/sys-nd/678.html)
- **Rates by Destination**:
  - **Singapore**: $1,500/day (limited carbon regulations)
  - **Japan**: $2,500/day (moderate carbon pricing mechanism)
  - **China**: $2,000/day (national carbon trading scheme)
- **Formula**: `Rate per Day × Voyage Days`

### 6. **Demurrage Costs**
- **Source**: [waytronsc.com](https://www.waytronsc.com/sys-nd/678.html)
- **Rate**: $125,000 per day
- **Laytime**: 36 hours each for loading and discharge
- **Probability of Delay**: 15%
- **Expected Delay**: 12 hours if delay occurs
- **Expected Cost**: $9,375 (probabilistic expected value)

### 7. **Letter of Credit (LC) Costs**
- **Source**: Standard international trade finance rates 2024
- **Rate**: 0.3% of transaction value (mid-range)
- **Minimum Fee**: $5,000
- **Components**:
  - Issuance Fee: 0.15% (issuing bank)
  - Confirmation Fee: 0.10% (confirming bank)
  - Negotiation Fee: 0.05% (negotiating bank)

---

## Example Calculation

### Scenario: USGC to Singapore
- **Cargo Volume**: 3,400,000 MMBtu
- **Baltic LNG Rate**: $18,000/day
- **Voyage Days**: 48 days
- **Purchase Cost**: $40,800,000 ($12/MMBtu)
- **Sale Value**: $51,000,000 ($15/MMBtu)

### Cost Breakdown:

| Component | Calculation | Amount |
|-----------|-------------|--------|
| **1. Base Freight** | $18,000 × 48 × 0.9 | **$777,600** |
| **2. Insurance** | Fixed per voyage | **$54,167** |
| **3. Brokerage** | $777,600 × 1.25% | **$9,720** |
| **4. Working Capital** | $40.8M × 6% × (48/365) | **$322,520** |
| **5. Carbon** | $1,500 × 48 | **$72,000** |
| **6. Demurrage (Expected)** | $125k × 0.5 day × 15% | **$9,375** |
| **7. LC Cost** | $51M × 0.3% | **$153,000** |
| **TOTAL** | | **$1,398,382** |
| **Per MMBtu** | $1,398,382 / 3.4M | **$0.411/MMBtu** |

### Cost Component Percentage Breakdown:
- Base Freight: 55.6%
- Working Capital: 23.1%
- LC Cost: 10.9%
- Carbon: 5.1%
- Insurance: 3.9%
- Demurrage: 0.7%
- Brokerage: 0.7%

---

## Example Calculation: USGC to Japan

### Scenario:
- **Cargo Volume**: 3,400,000 MMBtu
- **Baltic LNG Rate**: $18,000/day
- **Voyage Days**: 41 days
- **Route Scaling**: 1.0 (baseline)
- **Purchase Cost**: $40,800,000
- **Sale Value**: $54,400,000 ($16/MMBtu)

### Cost Breakdown:

| Component | Calculation | Amount |
|-----------|-------------|--------|
| **1. Base Freight** | $18,000 × 41 × 1.0 | **$738,000** |
| **2. Insurance** | Fixed per voyage | **$54,167** |
| **3. Brokerage** | $738,000 × 1.25% | **$9,225** |
| **4. Working Capital** | $40.8M × 6% × (41/365) | **$275,410** |
| **5. Carbon** | $2,500 × 41 | **$102,500** |
| **6. Demurrage (Expected)** | $125k × 0.5 day × 15% | **$9,375** |
| **7. LC Cost** | $54.4M × 0.3% | **$163,200** |
| **TOTAL** | | **$1,351,877** |
| **Per MMBtu** | $1,351,877 / 3.4M | **$0.398/MMBtu** |

---

## Example Calculation: USGC to China

### Scenario:
- **Cargo Volume**: 3,400,000 MMBtu
- **Baltic LNG Rate**: $18,000/day
- **Voyage Days**: 52 days
- **Route Scaling**: 1.05 (premium)
- **Purchase Cost**: $40,800,000
- **Sale Value**: $52,700,000 ($15.50/MMBtu)

### Cost Breakdown:

| Component | Calculation | Amount |
|-----------|-------------|--------|
| **1. Base Freight** | $18,000 × 52 × 1.05 | **$982,800** |
| **2. Insurance** | Fixed per voyage | **$54,167** |
| **3. Brokerage** | $982,800 × 1.25% | **$12,285** |
| **4. Working Capital** | $40.8M × 6% × (52/365) | **$349,150** |
| **5. Carbon** | $2,000 × 52 | **$104,000** |
| **6. Demurrage (Expected)** | $125k × 0.5 day × 15% | **$9,375** |
| **7. LC Cost** | $52.7M × 0.3% | **$158,100** |
| **TOTAL** | | **$1,669,877** |
| **Per MMBtu** | $1,669,877 / 3.4M | **$0.491/MMBtu** |

---

## Comparison Across Routes

| Route | Voyage Days | Total Cost | Per MMBtu | % vs Japan |
|-------|-------------|------------|-----------|------------|
| **Singapore** | 48 | $1,398,382 | $0.411 | +3.3% |
| **Japan** | 41 | $1,351,877 | $0.398 | Baseline |
| **China** | 52 | $1,669,877 | $0.491 | +23.5% |

### Key Insights:
1. **China is most expensive** despite shorter distance than initially expected, due to:
   - Longer voyage days (52 vs 41)
   - Route scaling premium (1.05×)
   - Higher working capital costs (longer voyage)

2. **Singapore benefits from**:
   - Route scaling discount (0.9×)
   - Lower carbon costs ($1,500/day vs $2,500)
   
3. **Major cost drivers**:
   - Base freight (50-60% of total)
   - Working capital (20-25%)
   - LC costs (10-12%)
   - Carbon costs growing in importance (5-6%)

---

## Implementation Notes

### In Code:
- All costs calculated in `src/cargo_optimization.py`
- Configuration in `config.py` with sources documented
- Method: `calculate_freight_cost()` returns detailed breakdown

### Flexibility:
- Each component can be toggled on/off if needed
- Rates can be updated as market conditions change
- Sources documented for transparency and validation

### Data Requirements:
- Baltic LNG freight rate (from data)
- Purchase cost (from Henry Hub calculation)
- Sale value (from destination pricing)
- Voyage days (from config by route)

---

## References

1. **Insurance Costs**: https://bplan.ai/blogs/running-expenses/lng-liquefied-natural-gas-shipping-and-transportation-running-expenses
2. **Demurrage**: https://www.waytronsc.com/sys-nd/678.html
3. **Carbon Costs**: https://www.mdpi.com/2077-1312/10/7/946
4. **IMO Regulations**: https://www.waytronsc.com/sys-nd/678.html
5. **General LNG Shipping**: https://financialmodelexcel.com/blogs/cost-open/lng-shipping-transportation
6. **Trade Finance**: Industry standard rates for international commodity trading

---

## Version
- **Last Updated**: October 16, 2025
- **Status**: Production Ready
- **Implementation**: Complete in `config.py` and `src/cargo_optimization.py`

