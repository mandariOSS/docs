---
title: Betrieb in Kubernetes
description: mandari mit Helm in einem Kubernetes-Cluster betreiben. Voraussetzungen, Installation, Migrationen, Worker, wichtige Werte, Aktualisieren, Sichern und Fehlersuche.
---

# Betrieb in Kubernetes

Für einen einzelnen Server ist [Docker Compose](index.md) der einfachere Weg. Kubernetes
lohnt sich, wenn Sie ohnehin einen Cluster betreiben, mehrere Instanzen der Anwendung
brauchen oder Datenbank und Cache als verwaltete Dienste nutzen wollen.

!!! note "Stand der Prüfung"
    Die CI prüft das Chart bei jeder Änderung statisch: `helm lint`, `helm template` für alle
    Werte-Dateien, `kubeconform` gegen Kubernetes 1.31 und den Gleichstand der Roh-Manifeste mit
    dem Chart. Ein automatischer Installationstest auf einem echten Cluster folgt noch.

## Voraussetzungen

- Kubernetes 1.27 oder neuer, `kubectl` mit Zugriff auf den Cluster
- Eine Speicherklasse (`kubectl get storageclass`)
- Für den Zugriff aus dem Internet ein Ingress-Controller und cert-manager. Den Ingress-Controller
  erkennt der Installer (auf k3s das mitgelieferte Traefik, sonst die Standardklasse des Clusters;
  `--ingress-class` gibt sie vor), er installiert aber selbst keinen. cert-manager bietet er an,
  falls er fehlt.
- Helm 3, wird bei Bedarf nachinstalliert

Bedarf: etwa 4 GB Arbeitsspeicher mit Volltextsuche, rund 2 GB ohne.

## Installation

=== "Mit dem Installer"

    ```bash
    git clone https://github.com/mandariOSS/mandari.git
    cd mandari
    ./install-k8s.sh
    ```

    Der Installer fragt Domain, Namespace, Speicherklasse und Administrationskonto ab,
    prüft die Cluster-Bausteine, installiert das Chart und wartet, bis die Anwendung läuft.

=== "Ohne Rückfragen"

    ```bash
    ./install-k8s.sh --unattended \
      --domain ris.meine-kommune.de \
      --namespace mandari \
      --tag latest
    ```

=== "Direkt mit Helm"

    ```bash
    helm upgrade --install mandari deploy/kubernetes/helm/mandari \
      --namespace mandari --create-namespace \
      --set domain=ris.meine-kommune.de \
      --set adminUser.email=admin@meine-kommune.de \
      --set adminUser.password='EinLangesPasswort' \
      --wait --wait-for-jobs
    ```

=== "Ohne Helm"

    ```bash
    kubectl create namespace mandari
    # In deploy/kubernetes/manifests/mandari.yaml alle Werte "BITTE-ERSETZEN-*" und die
    # Domain anpassen (Werte unter data: sind Base64-kodiert), dann:
    kubectl kustomize deploy/kubernetes/manifests | kubectl apply -f -
    kubectl -n mandari apply -f deploy/kubernetes/manifests/job-migrate.yaml
    ```

    Die Manifeste sind aus dem Chart erzeugt. Für Updates ist Helm deutlich bequemer.

| Schalter des Installers | Wirkung |
|-------------------------|---------|
| `--unattended` | ohne Rückfragen, Werte aus den übrigen Schaltern |
| `--domain`, `--namespace`, `--release`, `--tag` | Domain, Namespace, Name des Helm-Release, Version aller drei Images |
| `--storage-class`, `--ingress-class` | Speicherklasse bzw. Ingress-Klasse vorgeben |
| `--minimal` | ohne Elasticsearch |
| `--with-website`, `--website-host <host>` | Website mitinstallieren, auf Wunsch unter eigenem Hostnamen |
| `--dry-run` | nur die Manifeste zeigen |
| `--uninstall` | Release entfernen (siehe [Deinstallieren](#deinstallieren)) |

## Migrationen

Wie `update.sh` bei Docker Compose läuft die Migration in zwei Schritten:

| Wann | Job | Inhalt |
|------|-----|--------|
| Installation | `mandari-migrate` | `migrate`, Rollen, Suchindex, Administrationskonto, Website-Migrationen |
| Upgrade, vorher | `mandari-migrate-pre` | verträgliche Migrationen (`safemigrate`), Website-Migrationen |
| Upgrade, nachher | `mandari-migrate-post` | übrige Migrationen, Rollen, Suchindex, Administrationskonto |

Anwendung, Worker und Ingestor warten in einem Init-Container (`wait-for-schema`), bis alle Migrationen eingespielt sind, die vor dem Ausrollen laufen dürfen. So startet nichts gegen ein zu altes Schema, auch nicht bei der Erstinstallation mit `--wait`.

## Worker

Wie in Docker Compose laufen Ereignisse, Aufträge und alle [Zeitpläne](cron.md) in eigenen Deployments aus dem Anwendungs-Image, mit derselben Umgebung wie die Anwendung:

| Deployment | Aufgabe | Speichergrenze |
|------------|---------|----------------|
| `mandari-worker` | alle Rollen, Warteschlangen `default`, `mail`, `index`, `adapter` | 1Gi |
| `mandari-worker-heavy` | Texterkennung und KI (`ocr`, `ai`), abschaltbar mit `worker.heavy.enabled: false` | 3Gi |
| `mandari-worker-live` | Live-Übertragungen (`live`), abschaltbar mit `worker.live.enabled: false` | 512Mi |

Ist ein eigener Worker abgeschaltet, bedient der Hauptworker dessen Warteschlangen mit. `values-minimal.yaml` arbeitet so mit einem einzigen Worker. Start- und Liveness-Probe fragen `/health` auf Port 9091 ab; hängt eine Rolle länger als fünf Minuten, startet Kubernetes den Pod neu. Mehrere Repliken teilen sich die Arbeit ohne Doppelläufe.

Den Protokoll-Orchestrator für GPU-Rechenknoten (`minutes-orchestrator` in Docker Compose) bringt das Chart nicht mit.

## Nach der Installation

Die Domain muss auf den Ingress-Controller zeigen:

```bash
kubectl -n mandari get ingress mandari
```

**Zugangsdaten sichern.** Beim ersten Installieren erzeugt das Chart Schlüssel und
Passwörter; bei Upgrades bleiben sie erhalten.

```bash
kubectl -n mandari get secret mandari-secrets -o yaml > mandari-secrets-backup.yaml
```

!!! warning "Verschlüsselungsschlüssel"
    Der Eintrag `encryption-key` verschlüsselt Fachdaten wie Protokolle, Anträge und
    personenbezogene Felder. Geht er verloren, sind diese Daten unwiederbringlich
    unlesbar. Die Sicherung gehört in einen Passwortspeicher, nicht in die
    Versionsverwaltung. Der Schlüssel ist Base64 von genau 32 zufälligen Bytes
    (`openssl rand -base64 32`); das Chart prüft das Format.

## Wichtige Werte

| Wert | Vorgabe | Bedeutung |
|------|---------|-----------|
| `domain` | – | Adresse der Installation, Pflichtangabe |
| `image.tag` | `latest` | Version aller drei Images; im Betrieb fest setzen |
| `app.replicas` | `1` | Mehr als eine Instanz braucht `persistence.accessMode: ReadWriteMany` |
| `app.extraEnv`, `app.extraEnvFromSecret` | – | weitere [Umgebungsvariablen](konfiguration.md) für Anwendung und Worker |
| `postgres.enabled` | `true` | Auf `false` bei verwalteter Datenbank, dann `externalDatabase.url` setzen |
| `redis.enabled` | `true` | Analog mit `externalRedis.url` |
| `elasticsearch.enabled` | `true` | Aus: Suche läuft über die Datenbank, spart etwa 2 GB Arbeitsspeicher |
| `website.enabled`, `website.host` | `false`, leer | Website mitinstallieren; ohne eigenen Hostnamen nur clusterintern erreichbar |
| `ingress.className` | leer | Leer = Standard-Ingress-Klasse des Clusters (k3s: `traefik`) |
| `ingestor.syncInterval` | `15` | Grundtakt des Abgleichs je Quelle werktags 7 bis 19 Uhr in Minuten; sonst stündlich, am Wochenende alle 2 Stunden |
| `ingestor.fullSyncHour`, `ingestor.concurrent` | `3`, `10` | Beginn des nächtlichen Fensters für Vollabgleiche, gleichzeitige Anfragen je Lauf |
| `ingestor.extraEnv` | – | Umgebungsvariablen nur für den Ingestor |
| `worker.enabled`, `worker.replicas` | `true`, `1` | Worker für Ereignisse, Aufträge und Zeitpläne |
| `worker.heavy.enabled`, `worker.live.enabled` | `true`, `true` | eigene Worker für Texterkennung und KI bzw. Live-Übertragungen |
| `worker.affinity` | `{}` | z. B. `podAffinity` zur Anwendung bei `ReadWriteOnce` (siehe [Skalieren](#skalieren)) |
| `files.textExtractionRunner` | `ingestor` | Wer den Text der Dokumente erkennt; `worker` braucht zusätzlich `TASKS_BACKEND=journal` in `app.extraEnv` |
| `events.producers`, `events.changesFeed` | `false` | Ereignisse zum RIS-Bestand bzw. Änderungsfeed einschalten (siehe unten) |
| `liveStreams.enabled` | `false` | Live-Übertragungen (`LIVE_UEBERTRAGUNG_AKTIV`) |
| `mail.fromEmail`, `mail.messageIdDomain` | leer | Absender und Domain für Message-ID und EHLO |
| `persistence.files.size` | `50Gi` | Heruntergeladene Dokumente; wächst mit der Zahl der Kommunen |
| `secrets.existingSecret` | leer | eigenes Secret statt erzeugter Schlüssel |
| `logging.format` | `json` | Siehe [Logging und Tracing](logging-tracing.md) |
| `tracing.otlpEndpoint` | leer | Gesetzt: OpenTelemetry aktiv |
| `networkPolicy.enabled` | `false` | Schränkt den Zugriff auf Datenbank, Cache und Suchindex ein |

Vollständige Liste im Chart unter `deploy/kubernetes/helm/mandari/values.yaml`, Beschreibung in `deploy/kubernetes/README.md`. Vorlagen für kleine und große Installationen liegen als `values-minimal.yaml` und `values-production.yaml` daneben.

**Ereignistechnik einschalten:** erst `events.producers` (Ereignisse zum RIS-Bestand), danach `events.changesFeed` (Änderungsfeed und Snapshot). Beides erst, wenn der Worker läuft (`kubectl -n mandari get pods -l app.kubernetes.io/component=worker`).

## Aktualisieren

Die Migrationen laufen vor und nach dem Ausrollen von selbst (siehe [Migrationen](#migrationen)):

```bash
helm upgrade mandari deploy/kubernetes/helm/mandari -n mandari \
  --reset-then-reuse-values --set image.tag=v0.11.0 --wait --wait-for-jobs
```

`--reset-then-reuse-values` (Helm 3.14 oder neuer) übernimmt neue Standardwerte des Charts und behält Ihre eigenen Werte.

## Skalieren

Mehr Repliken der Anwendung brauchen eine Speicherklasse mit `ReadWriteMany` (zum Beispiel NFS, CephFS, Longhorn). Der Ingestor bleibt bei einer Instanz, damit Quellen nicht doppelt abgefragt werden. Die Worker binden `media` und `files` ein wie die Anwendung: Mit `ReadWriteOnce` (Standard) müssen auf einem Cluster mit mehreren Knoten Anwendung, Ingestor und Worker auf demselben Knoten laufen, sonst bleibt ein Pod mit „Multi-Attach“ hängen. Dafür `worker.affinity` und `app.affinity` auf denselben Knoten legen oder `ReadWriteMany` verwenden.

## Sichern

```bash
# Datenbank
kubectl -n mandari exec statefulset/mandari-postgres -- \
  pg_dump -U mandari mandari | gzip > mandari-$(date +%F).sql.gz

# Dateien: die Volumes mandari-media und mandari-files in die Sicherung des
# Clusters aufnehmen (z. B. Velero) oder aus einem Pod kopieren
kubectl -n mandari cp mandari-<pod>:/app/media ./media-backup
```

Dazu gehört die Sicherung des Secrets (siehe oben). Siehe auch [Updates und Backups](updates-backups.md).

## Fehlersuche

| Beobachtung | Ursache und Abhilfe |
|---|---|
| Pods bleiben `Pending` | Keine passende Speicherklasse oder zu wenig Ressourcen: `kubectl -n mandari describe pod <name>` |
| Pods bleiben in `Init:0/1` | Sie warten auf das Schema: `kubectl -n mandari logs <pod> -c wait-for-schema`, dann den Migrations-Job prüfen |
| Migrations-Job schlägt fehl | Datenbank nicht erreichbar oder Zugangsdaten passen nicht: `kubectl -n mandari logs job/mandari-migrate --all-containers` |
| Website-Migration scheitert („database … does not exist“) | Der mitgelieferte Postgres legt `mandari_website` nur beim ersten Start an. Nachträglich: `kubectl -n mandari exec statefulset/mandari-postgres -- createdb -U mandari mandari_website` |
| Anwendung startet nicht (`CrashLoopBackOff`) | Meist die Datenbankverbindung: `kubectl -n mandari logs deploy/mandari` |
| Kein Zertifikat | cert-manager oder ClusterIssuer fehlt: `kubectl describe certificate -n mandari` |
| 502 vom Ingress | Anwendung noch nicht bereit: `kubectl -n mandari get pods` |
| Elasticsearch startet nicht | Zu wenig Arbeitsspeicher: `elasticsearch.javaOpts` senken oder abschalten |

Logs der Dienste:

```bash
kubectl -n mandari logs -f deploy/mandari
kubectl -n mandari logs -f deploy/mandari-ingestor
kubectl -n mandari logs -f deploy/mandari-worker
kubectl -n mandari logs -f deploy/mandari-worker-heavy
kubectl -n mandari logs -f deploy/mandari-worker-live
```

Ohne Ingress erreichen Sie die Installation direkt:

```bash
kubectl -n mandari port-forward svc/mandari 8080:80
```

## Deinstallieren

```bash
./install-k8s.sh --uninstall --namespace mandari
```

Daten und Zugangsdaten bleiben absichtlich erhalten. Vollständig entfernen, nicht
umkehrbar:

```bash
kubectl delete namespace mandari
```
