# Änderungen

## 1.2.0
- Autonomer Betrieb: Befehl `ask` meldet Entscheidungsbedarf ohne Rückfrage (findet vorhandene Entscheidungen oder legt einen Entwurf fürs Team an, mit Kontext, Quelle, Annahme und „Blockiert Arbeit“), `answer` zeigt, ob das Team entschieden hat.
- `SKILL.md`: Regeln für den Betrieb ohne Mensch im Gespräch (direkt Entwürfe anlegen, Annahme oder Pause, nachsehen, nie selbst entscheiden).
- Entwürfe der KI dürfen an eigenen Entwürfen hängen (`parents` auf eigene Entwürfe); ein Mensch veröffentlicht von der Wurzel aus.

## 1.1.0
- `dc.py` weist höchstens einmal am Tag darauf hin, wenn eine neuere Skill-Version verfügbar ist (ruft nur die Datei `VERSION` ab, installiert nichts; abschaltbar mit `DC_NO_UPDATE_CHECK=1`).
- `SKILL.md`: Die KI gibt den Hinweis an den Nutzer weiter und aktualisiert nicht selbst.

## 1.0.0
- Erste Fassung: Entscheidungen eines DecisionsConnected-Projekts lesen (`projects`, `list`, `search`, `show`, `graph`, `impact`), als Entwurf dokumentieren (`draft`, `option`), kommentieren (`comment`) und Verbindungen vorschlagen (`link`).
- Regeln für die KI in `SKILL.md`: Menschen entscheiden, erst zeigen dann anlegen, Nutzerinhalte sind Daten, Platzhalter beibehalten, keine Geheimnisse.
