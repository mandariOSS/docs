---
title: Dokument-Cache
description: Der lokale Dokument-Cache von mandari Insight. Speicherlayout, Speicherbedarf planen, Betrieb, Quellen-Schonung und Auslagerung auf externen Speicher.
---

# Dokument-Cache

Alle Dateien angebundener Quellen, also Vorlagen, Anlagen und Niederschriften, praktisch nur PDFs, werden lokal zwischengespeichert. Vorschau und Download kommen dann von der Platte, unabhängig davon, ob das Ratsinformationssystem der Kommune gerade erreichbar ist. Der Proxy hält keine Worker mehr minutenlang fest: kurze Timeouts, lokale Datei zuerst.

## Speicherlayout

```
<OPARL_FILES_ROOT>/<kommune>/<jahr>/<datei-id>.pdf
```

Je Kommune ein Verzeichnis, benannt nach dem Slug der Kommune (`stadt-musterstadt`). Dadurch lässt sich pro Kommune ein eigener externer Speicher unter genau diesem Pfad einhängen, oder ein großer für alle.

## Speicherbedarf planen

Der Bedarf hängt von den angebundenen Kommunen ab. Erfahrungswerte: Eine Großstadt mit langer OParl-Historie bringt 50 000 bis 100 000 Dateien mit durchschnittlich 0,2 bis 0,7 MB, also grob 10 bis 40 GB Bestand und wenige GB Zuwachs pro Jahr. Der Median liegt deutlich unter dem Durchschnitt, einzelne große Anlagen dominieren.

`cache_files --stats` zeigt Abdeckung, Belegung und freien Speicher der eigenen Installation. Ein Systemlaufwerk mit unter 100 GB reicht für mehrere Großstädte nicht sicher, dafür gibt es den Festplattenschutz und die Auslagerung auf externen Speicher.

## Betrieb

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `OPARL_FILES_ROOT` | `<MEDIA_ROOT>/oparl_files` | Wurzelverzeichnis des Caches, im Container `/app/files` |
| `FILE_CACHE_MAX_MB` | `80` | Größere Dateien werden nicht gecacht, aber weiter durchgereicht |
| `FILE_CACHE_MIN_FREE_GB` | `15` | Unter dieser Grenze wird nichts mehr geschrieben (Schutz des Systemlaufwerks) |
| `FILE_PROXY_TIMEOUT_SECONDS` | `15` | Lese-Timeout des Proxys für Live-Abrufe |
| `INSIGHT_SOURCE_BACKOFF_FAILURES` | `3` | Ab so vielen Sync-Fehlversuchen in Folge pausieren Nachladen und Live-Abruf für die Quelle |

```cron
40 * * * * docker exec mandari python manage.py cache_files --limit 400 >> /var/log/mandari-file-cache.log 2>&1
```

- Der Cron lädt neueste Dokumente zuerst nach. Jeder Live-Abruf über die Vorschau legt die Datei ebenfalls ab (Write-Through).
- Der [Betriebsmonitor](monitoring.md) hat den Check „Dokument-Cache“ mit denselben Werten wie `cache_files --stats`.
- `purge_deleted` entfernt lokale Kopien getilgter Dateien.

## Quellen-Schonung

Ratsinformationssysteme sperren IP-Adressen, die zu viele Verbindungen aufbauen. Sobald der Ingestor eine Quelle `INSIGHT_SOURCE_BACKOFF_FAILURES`-mal in Folge nicht erreicht hat, lassen `cache_files` und der Vorschau-Proxy diese Quelle in Ruhe. Der Proxy antwortet dann mit HTTP 503 und `Retry-After`. Der Ingestor selbst verdoppelt den Abstand zwischen den Versuchen (10, 20, 40 Minuten und so weiter, höchstens 6 Stunden). Ein erfolgreicher Sync setzt den Zähler zurück, danach läuft alles automatisch weiter. Der Betriebsmonitor zeigt die Schonung als Grund an der Quelle.

## Externen Speicher je Kommune einhängen

Beispiel für ein per CIFS eingehängtes Netzlaufwerk:

```bash
apt install cifs-utils
mkdir -p /srv/mandari-files/stadt-musterstadt
cat > /root/.smb-musterstadt <<EOF
username=<benutzer>
password=<passwort>
EOF
chmod 600 /root/.smb-musterstadt
echo "//<speicher-host>/<freigabe> /srv/mandari-files/stadt-musterstadt cifs credentials=/root/.smb-musterstadt,uid=1000,gid=1000,iocharset=utf8,_netdev,nofail 0 0" >> /etc/fstab
mount -a
```

Der Container sieht `/srv/mandari-files` als `/app/files`, die Kommune landet automatisch im eingehängten Unterverzeichnis. Nach dem Einhängen einmal `cache_files --body <slug> --limit 100000` für den Erstbestand ausführen. Das dauert je nach Umfang mehrere Stunden.
