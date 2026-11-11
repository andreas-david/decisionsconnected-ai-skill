# Gute Entscheidungen aufschreiben

## Titel
Eine **Frage**, die sich mit einer der Optionen beantworten lässt: „Welche Datenbank nehmen wir?", „Wann darf eine Verbindung gelöst werden?". Keine Aussage („Wir nehmen PostgreSQL"), keine Aufgabe („PostgreSQL einrichten").

## Optionen
- Mindestens **zwei**, kurz und gegeneinander abgrenzbar (Titel bis etwa 80 Zeichen). Längeres in `description`.
- Immer auch die Gegenoption bedenken: „Beim Bisherigen bleiben", „Nichts tun", „Später entscheiden".
- Eine Option ist eine Entscheidung, kein Argument. Argumente gehören in die Beschreibung.

## Beschreibung (Kontext)
- Worum geht es, warum jetzt, welche Kriterien zählen (Kosten, Aufwand, Risiko, Datenschutz)?
- **Quelle** nennen, wenn aus Code, Dokument oder Gespräch dokumentiert wird („aus PR 123", „Gespräch vom 10.11.").
- Beim **Nachtragen** schon getroffener Entscheidungen: „Dokumentiert aus: … Laut Projekt gewählt: … Begründung: …". Es bleibt ein Entwurf; ein Mensch trägt sie nach.
- Sachlich, ohne Wertung, ohne Namen einzelner Personen, soweit nicht nötig.
- Keine Geheimnisse, keine Zugangsdaten.

## Strang (Startmarke)
Nur an **Startkarten** (ohne Vorgänger): ein kurzer Name für einen Entscheidungspfad („Hosting", „Landingpage", „API"). Die Folgen gehören über ihre Verbindungen dazu. Bestehende Strangnamen mit `list --compact` ansehen und denselben Namen verwenden, nicht Varianten erfinden.

## Stichtag
`dueDate` (JJJJ-MM-TT) nur setzen, wenn es einen echten Termin gibt.

## Vor dem Anlegen prüfen
- Gibt es die Entscheidung schon (`search`)? Dann kommentieren statt doppelt anlegen.
- Hängt sie an einer bestehenden Entscheidung (Vorgänger, Option, Typ)?
- Dem Nutzer zeigen und Freigabe holen.
