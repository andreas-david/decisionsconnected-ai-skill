# Verknüpfungen

Eine **Folgeentscheidung** hängt an einer **Option** einer **Vorgängerentscheidung**. Die Verbindung wird **aus Sicht der Folge** gesetzt und gilt für **jede** Option des Vorgängers: Die gewählte Option bekommt `type`, alle anderen `others` (Standard `no_effect`).

| Typ | Bedeutung aus Sicht der Folge | Wirkung bei Änderung des Vorgängers |
|---|---|---|
| `based_on` | „Ich basiere darauf." Diese Option ist die Grundlage. | Die Folge ist betroffen und muss angepasst werden. |
| `check` | „Ich prüfe das." | Die Folge wird als „zu prüfen" markiert. |
| `no_effect` | „Ich bin davon unabhängig." | Keine Auswirkung. |
| `blocks` | „Ich blockiere das." Die Folge sperrt diese Option des Vorgängers. | Für diese Option lässt sich nicht entscheiden, solange die Verbindung besteht. |
| `ends` | „Dann entfalle ich." Wird diese Option gewählt, wird die Folge hinfällig. | Die Folge samt Teilbaum entfällt. |

## Beispiele
- „Welche Datenbank?" (Optionen: PostgreSQL, MariaDB). Die Folge „Wie sichern wir die Datenbank?" baut auf PostgreSQL auf: `option` = Schlüssel von PostgreSQL, `type` = `based_on`, `others` = `no_effect`.
- „Brauchen wir ein Kundenportal?" (Ja/Nein). Die Folge „Wie authentifizieren sich Kunden?" entfällt bei „Nein": `option` = Schlüssel von „Nein", `type` = `ends`; `others` = `based_on` (bei „Ja" ist sie Grundlage).

## Regeln
- Ein Vorgänger darf **veröffentlicht** oder ein **eigener Entwurf** der KI sein; die Folge darf ein Entwurf sein. Mehrere zusammengehörige Entwürfe werden gleich verbunden (zuerst die Wurzel anlegen, dann die Folgen). Ein Mensch veröffentlicht von der Wurzel aus.
- Keine Kreise (eine Folge kann nicht ihr eigener Vorfahr sein).
- Verbindungen, die die KI vorschlägt, sind **angefragt**. Ein Mensch mit dem Recht „Verbindungen annehmen" nimmt sie an oder lehnt sie ab.
- Optionsschlüssel stehen in `show`/`list` unter `options[].key`.
