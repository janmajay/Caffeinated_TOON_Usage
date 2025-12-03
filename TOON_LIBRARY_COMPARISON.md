# TOON Library Comparison: toon-format vs toon-python

## Summary
**`toon-format` and `toon-python` are THE SAME library!** They both refer to the official Python implementation of the TOON (Token-Oriented Object Notation) specification.

## Current Setup
You are currently using:
- **Package name on PyPI:** `toon-format`
- **Import name in Python:** `toon_format`
- **Version:** 0.9.0b1 (beta)
- **GitHub:** https://github.com/toon-format/toon-python

## Key Findings

### 1. No Alternative Library
There is **only ONE** official TOON library for Python:
- PyPI package: `toon-format`
- The term "toon-python" is often used to refer to the same library (it's the Python implementation of TOON)
- There is a separate `toon` package on PyPI, but it's for **neuroscience input device polling** (completely unrelated)

### 2. Compression Performance
According to research, TOON achieves:
- **30-60% token reduction** compared to JSON (typical)
- **42.3% reduction** in benchmark with 100 GitHub records (15,145 → 8,745 tokens)
- **46.3% average reduction** across various LLM models
- **59% savings** for time-series analytics data
- **56% reduction** in production deployment (1,344 → 589 tokens)
- **65.8% character reduction** in specific test cases

### 3. How TOON Achieves Compression
- **Eliminates redundant punctuation:** No curly braces, square brackets, or most quotes
- **Indentation-based nesting:** Like YAML (whitespace for structure)
- **Tabular array optimization:** CSV-like format for uniform arrays (field names declared once)
- **Semantic clarity:** Maintains readability for LLMs while reducing tokens

### 4. When TOON Works Best
✅ **Excellent for:**
- Tabular data (arrays of similar objects)
- Repetitive structures
- Time-series data
- E-commerce orders
- API responses with consistent schemas

⚠️ **Less effective for:**
- Deep nesting with varied structures
- Non-uniform data
- Small payloads (overhead not worth it)

## Recommendation

### ✅ Keep Your Current Setup
**You should KEEP using `toon-format` (0.9.0b1)** because:

1. **It's the official and only TOON library** for Python
2. **It's already working** and integrated with your code
3. **No better alternative exists** - this IS the best option
4. **Active development** - it's on GitHub and maintained
5. **Your current results are good** - you're seeing ~7-8% savings, which is reasonable for your data structure

### 📊 Your Current Performance
From your test:
- JSON: 6,221 tokens
- TOON: 5,744 tokens
- Savings: 477 tokens (7.67%)

This is **lower than the 30-60% benchmark** because your data structure might have:
- Deep nesting
- Non-uniform objects
- Less tabular/repetitive data

### 💡 To Improve Compression Rate
If you want better savings, consider:
1. **Restructure data to be more tabular** (arrays of similar objects)
2. **Flatten nested structures** where possible
3. **Use consistent field names** across objects
4. **Increase the number of users** (more repetitive data = better compression)

## Conclusion
**No need to change anything!** You're already using the best and only TOON library available. The 7.67% savings you're seeing is legitimate and will scale with larger, more repetitive datasets.
