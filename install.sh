#!/bin/bash
# Aufruf: skill/install.sh /pfad/zum/projekt
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:?Pfad zum Projekt angeben}"
[ -d "$TARGET" ] || { echo "Ordner nicht gefunden: $TARGET" >&2; exit 1; }
mkdir -p "$TARGET/.claude/skills"
rm -rf "$TARGET/.claude/skills/decisionsconnected"
cp -R "$HERE/decisionsconnected" "$TARGET/.claude/skills/decisionsconnected"
chmod +x "$TARGET/.claude/skills/decisionsconnected/scripts/dc.py"
echo "Skill installiert: $TARGET/.claude/skills/decisionsconnected"
echo "Nächster Schritt: DC_API_TOKEN in $TARGET/.claude/settings.local.json hinterlegen (nicht einchecken), siehe $HERE/README.md"
