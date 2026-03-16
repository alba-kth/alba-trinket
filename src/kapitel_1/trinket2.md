---
---

# Minusgrader i Stockholm

## Description
SMHI har mätt medeltemperaturen i Stockholm (Observatorielunden) varje
år sedan 1900. Dessa data är sorterade efter år i filen
smhi_temperaturer.txt

Skriv ett program som skriver ut de år som som det varit minusgrader i
Stockholm. 

## Files

#### filinlas.py
```python
def read_years(filename):
    uppslagslista = {}
    with open(filename, 'r') as fil:
        rows = fil.readlines()
    for row in rows:
        year, temp = row.strip().split()
        uppslagslista[year] = float(temp)
    return uppslagslista

```

#### smhi_temperaturer.txt
```
1993    0.00
1994    -6.10
1995    1.00
1996    -6.10
1997    0.40
```

## Main Code
```python
import filinlas

temperaturer = filinlas.read_years('smhi_temperaturer.txt')
for year, temp in temperaturer.items():
    if temp < 0:
        print(year)
```

