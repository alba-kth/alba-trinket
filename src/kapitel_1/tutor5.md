---
output: text
---
# Inmatning med input()

## Description
Programmet frågar användaren efter namn och födelseår och skriver ut en hälsning med åldern.
Svara på frågorna i output-fönstret och tryck Enter efter varje svar.

## Main Code
```python
namn = input("Vad heter du? ")
ar = int(input("Vilket år är du född? "))
alder = 2026 - ar
print(f"Hej {namn}! Du är {alder} år gammal.")
```
