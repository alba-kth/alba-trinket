---
---

# if __name__ == "__main__"

## Description
När Python importerar en fil körs all kod i filen direkt.
Det betyder att testkod som inte skyddas med `if __name__ == "__main__":` körs
även vid import — vilket ofta är oönskat.

Kör programmet och se vad som händer. Vilken fil orsakar oönskad utskrift vid import?

## Files

### med_guard.py
```python
def halsa(namn):
    return "Hej, " + namn + "!"

if __name__ == "__main__":
    # Den här koden körs INTE vid import
    r = halsa("världen")
    if r == "Hej, världen!":
        print("testet lyckades")
    else:
        print(f"testet misslyckades: förväntade 'Hej, världen!' men fick '{r}'")
```

### utan_guard.py
```python
def dubblera(x):
    return x * 2

# Den här koden körs ALLTID — även vid import!
r = dubblera(5)
if r == 10:
    print("testet lyckades")
else:
    print(f"testet misslyckades: förväntade 10 men fick {r}")
```

## Main Code
```python
import med_guard
import utan_guard

print("################# main #################")
print(med_guard.halsa("kursare"))
print(utan_guard.dubblera(21))
```
