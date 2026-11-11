# DecisionsConnected: Skill für KI-Assistenten

Ein Skill für [Claude Code](https://claude.com/claude-code) (und kompatible Werkzeuge), der eine KI zum **Teilnehmer eines [DecisionsConnected](https://www.decisionsconnected.com)-Projekts** macht: Sie liest Projektentscheidungen, dokumentiert neue als **Entwurf**, kommentiert und schlägt Verbindungen vor. **Menschen entscheiden.** Die KI stimmt nie ab, entscheidet nie, veröffentlicht nie.

*English: A skill that lets an AI assistant read, draft, comment on and link decisions in a DecisionsConnected project. Humans decide. German-language documentation.*

Version 1.0.0 · Lizenz MIT

## Was du brauchst
- Ein Projekt in DecisionsConnected und die Rolle **Projektleitung**.
- Der KI-Zugang deiner Firma ist unter *Konto* erlaubt (Verwaltung der Firma).
- Python 3 (nur Standardbibliothek).

## Einrichten
1. In DecisionsConnected im Projekt **Beteiligte → KI-Teilnehmer → KI hinzufügen**:
   - Namen wählen (so erscheint die KI in Entscheidungen und Kommentaren, zum Beispiel „Claude" oder „Claude (KI)"),
   - Modus wählen: **pseudonymisiert** (über [AI Data Veil](https://aidataveil.eu), die KI sieht nur Platzhalter) oder **Klartext** mit Bestätigung einer sicheren KI,
   - Datenumfang und Rechte (Entwürfe, Kommentare) wählen.
   Der Schlüssel (`dct_…`) wird **einmal** angezeigt.
2. Skill ins Projekt installieren:
   ```bash
   git clone https://github.com/andreas-david/decisionsconnected-ai-skill.git
   decisionsconnected-ai-skill/install.sh /pfad/zum/projekt
   ```
   Das legt `.claude/skills/decisionsconnected/` im Projekt an. (Oder den Ordner `decisionsconnected/` von Hand dorthin kopieren.)
3. Den Schlüssel hinterlegen, **nicht einchecken**: in `/pfad/zum/projekt/.claude/settings.local.json`
   ```json
   { "env": { "DC_API_TOKEN": "dct_…" } }
   ```
   und `.claude/settings.local.json` in die `.gitignore` des Projekts aufnehmen.
4. In Claude Code im Projekt fragen: „Welche Entscheidungen sind offen?", „Gibt es schon eine Entscheidung zu X?", „Dokumentiere, dass wir Y gewählt haben."

Jedes Projekt braucht **seinen eigenen KI-Teilnehmer und Schlüssel**.

## Was die KI darf
| | |
|---|---|
| Immer | Entscheidungen, Optionen, Verbindungen, Folgen lesen (je nach Datenumfang auch Beschreibungen, Begründungen, Kommentare) |
| Mit Recht „Entwürfe" | Entscheidungsentwurf mit Optionen, Strang und Vorgängern anlegen; Verbindungen vorschlagen (bleiben „angefragt") |
| Mit Recht „Kommentare" | Kommentieren |
| Nie | Abstimmen, entscheiden, veröffentlichen, Verbindungen annehmen, wieder öffnen, Änderungsanträge, Rechte ändern |

Entwürfe prüft und veröffentlicht ein Mensch. Verantwortlich ist die Person, die die KI ins Projekt geholt hat.

## Datenschutz
Die Inhalte eines Projekts gehen an den Anbieter deiner KI. Im Modus *pseudonymisiert* ersetzt DecisionsConnected Namen, Firmen und Projekte vorher durch Platzhalter wie `[PERSON_1]`; die Zuordnung bleibt in DecisionsConnected. Pseudonymisierung ist keine Anonymisierung. Prüfe mit der Vorschau („Was sieht die KI?"), was die KI zu sehen bekommt. Die Firma bleibt verantwortlich (Rechtsgrundlage, Auftragsverarbeitung).

## Sicherheit
- Der Schlüssel gehört **nie** in dieses Repository, in Chats, Tickets oder Entscheidungen. `scripts/dc.py` liest ihn nur aus `DC_API_TOKEN`.
- Texte aus Entscheidungen sind Daten, keine Anweisungen. Der Skill weist die KI an, sie nicht zu befolgen.
- Schlüssel lassen sich in DecisionsConnected jederzeit erneuern oder mit „KI entfernen" löschen.

## Inhalt
- `decisionsconnected/SKILL.md`: Anleitung und Regeln für die KI
- `decisionsconnected/scripts/dc.py`: Befehle für die Schnittstelle (`python3 scripts/dc.py --help`)
- `decisionsconnected/references/`: Schnittstelle, Leitfaden für gute Entscheidungen, Verknüpfungstypen
- `install.sh`: kopiert den Skill in ein Projekt

## Lizenz
MIT, siehe [LICENSE](LICENSE). Die Lizenz gilt für diesen Skill, nicht für den Dienst DecisionsConnected (eigene Bedingungen) und nicht für den Namen „DecisionsConnected" oder das Logo.
