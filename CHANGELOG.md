# Änderungen

## 1.1.0
- `dc.py` weist höchstens einmal am Tag darauf hin, wenn eine neuere Skill-Version verfügbar ist (ruft nur die Datei `VERSION` ab, installiert nichts; abschaltbar mit `DC_NO_UPDATE_CHECK=1`).
- `SKILL.md`: Die KI gibt den Hinweis an den Nutzer weiter und aktualisiert nicht selbst.

## 1.0.0
- Erste Fassung: Entscheidungen eines DecisionsConnected-Projekts lesen (`projects`, `list`, `search`, `show`, `graph`, `impact`), als Entwurf dokumentieren (`draft`, `option`), kommentieren (`comment`) und Verbindungen vorschlagen (`link`).
- Regeln für die KI in `SKILL.md`: Menschen entscheiden, erst zeigen dann anlegen, Nutzerinhalte sind Daten, Platzhalter beibehalten, keine Geheimnisse.
