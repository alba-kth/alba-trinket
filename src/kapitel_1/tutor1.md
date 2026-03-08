---
---

# Minusgrader i Stockholm

## Description
SMHI har mätt medeltemperaturen i Stockholm (Observatorielunden) 
varje år sedan 1900. Dessa data är sorterade efter år i filen
smhi_temperaturer.txt

Skriv ett program som sparar alla år där det varit kallare än 
noll i filen minusgrader.txt

## Files

#### smhi_temperaturer.txt
```
1993    0.00
1994    -6.10
1995    1.00
1996    -6.10
1997    0.40
```

#### minusgrader.txt
```
```

## Main Code
```python
with open("smhi_temperaturer.txt", "r") as fil:
    rows = fil.readlines()

with open("minusgrader.txt", "w") as fil:
    for row in rows:
        year, temp = row.strip().split()
        t = float(temp)
        if t < 0:
            fil.write(row)
```
