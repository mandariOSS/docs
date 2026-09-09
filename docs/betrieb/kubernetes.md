---
title: Betrieb in Kubernetes
description: mandari mit Helm in einem Kubernetes-Cluster betreiben. Voraussetzungen, Installation, wichtige Werte, Backup und Fehlersuche.
---

# Betrieb in Kubernetes

Für einen einzelnen Server ist [Docker Compose](index.md) der einfachere Weg. Kubernetes
lohnt sich, wenn Sie ohnehin einen Cluster betreiben, mehrere Instanzen der Anwendung
brauchen oder Datenbank und Cache als verwaltete Dienste nutzen wollen.

## Voraussetzungen

- Kubernetes 1.27 oder neuer, `kubectl` mit Zugriff auf den Cluster
- Eine Speicherklasse (`kubectl get storageclass`)
- Ein Ingress-Controller und cert-manager für HTTPS. Fehlen sie, bietet der Installer an,
  ingress-nginx und cert-manager mitzuinstallieren.
- Helm 3 – wird bei Bedarf nachinstalliert

Bedarf: etwa 4 GB Arbeitsspeicher mit Volltextsuche, rund 2 GB ohne.

## Installation

=== "Mit dem Installer"

    ```bash
    git clone https://github.com/mandariOSS/mandari.git
    cd mandari
    ./install-k8s.sh
    ```

    Der Installer fragt Domain, Namespace, Speicherklasse und Administrationskonto ab,
    prüft die Cluster-Bausteine und wartet, bis die Anwendung läuft.

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
      --wait
    ```

=== "Ohne Helm"

    ```bash
    kubectl create namespace mandari
    # In deploy/kubernetes/manifests/mandari.yaml die Werte "BITTE-ERSETZEN-*"
    # und die Domain anpassen, dann:
    kubectl kustomize deploy/kubernetes/manifests | kubectl apply -f -
    kubectl -n mandari apply -f deploy/kubernetes/manifests/job-migrate.yaml
    ```

Weitere Schalter des Installers: `--minimal` (ohne Elasticsearch), `--with-website`,
`--dry-run` (zeigt nur die Manifeste), `--storage-class`, `--uninstall`.

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
    Versionsverwaltung.

## Wichtige Werte

| Wert | Vorgabe | Bedeutung |
|------|---------|-----------|
| `domain` | – | Adresse der Installation, Pflichtangabe |
| `image.tag` | `latest` | Version aller Images; im Betrieb fest setzen |
| `app.replicas` | `1` | Mehr als eine Instanz braucht `persistence.accessMode: ReadWriteMany` |
| `postgres.enabled` | `true` | Auf `false` bei verwalteter Datenbank, dann `externalDatabase.url` setzen |
| `redis.enabled` | `true` | Analog mit `externalRedis.url` |
| `elasticsearch.enabled` | `true` | Aus: Suche läuft über die Datenbank, spart etwa 2 GB Arbeitsspeicher |
| `website.enabled` | `false` | Marketing-Website mitinstallieren |
| `ingestor.syncInterval` | `15` | Minuten zwischen zwei OParl-Synchronisationen |
| `persistence.files.size` | `50Gi` | Heruntergeladene Dokumente; wächst mit der Zahl der Kommunen |
| `logging.format` | `json` | Siehe [Logging und Tracing](logging-tracing.md) |
| `networkPolicy.enabled` | `false` | Schränkt den Zugriff auf Datenbank, Cache und Suchindex ein |

Vollständige Liste im Chart unter `deploy/kubernetes/helm/mandari/values.yaml`. Vorlagen
für kleine und große Installationen liegen als `values-minimal.yaml` und
`values-production.yaml` daneben.

## Aktualisieren

Migrationen laufen automatisch als Job, bevor die neuen Pods starten:

```bash
helm upgrade mandari deploy/kubernetes/helm/mandari -n mandari \
  --reuse-values --set image.tag=v1.2.3 --wait
```

## Sichern

```bash
# Datenbank
kubectl -n mandari exec statefulset/mandari-postgres -- \
  pg_dump -U mandari mandari | gzip > mandari-$(date +%F).sql.gz

# Dateien: die Volumes mandari-media und mandari-files in die Sicherung des
# Clusters aufnehmen (z. B. Velero) oder aus einem Pod kopieren
kubectl -n mandari cp mandari-<pod>:/app/media ./media-backup
```

Siehe auch [Updates und Backups](updates-backups.md).

## Fehlersuche

| Beobachtung | Ursache und Abhilfe |
|---|---|
| Pods bleiben `Pending` | Keine passende Speicherklasse oder zu wenig Ressourcen: `kubectl -n mandari describe pod <name>` |
| Migrations-Job schlägt fehl | Datenbank nicht erreichbar: `kubectl -n mandari logs job/mandari-migrate` |
| Anwendung startet nicht | Meist die Datenbankverbindung: `kubectl -n mandari logs deploy/mandari` |
| Kein Zertifikat | cert-manager oder ClusterIssuer fehlt: `kubectl describe certificate -n mandari` |
| Elasticsearch startet nicht | Zu wenig Arbeitsspeicher: `elasticsearch.javaOpts` senken oder abschalten |

Ohne Ingress erreichen Sie die Installation direkt:

```bash
kubectl -n mandari port-forward svc/mandari 8080:80
```

## Deinstallieren

```bash
./install-k8s.sh --uninstall --namespace mandari
```

Daten und Zugangsdaten bleiben absichtlich erhalten. Vollständig entfernen – nicht
umkehrbar:

```bash
kubectl delete namespace mandari
```
