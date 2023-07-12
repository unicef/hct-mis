{{/*
Expand the name of the chart.
*/}}
{{- define "hope.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hope.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hope.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hope.labels" -}}
helm.sh/chart: {{ include "hope.chart" . }}
{{ include "hope.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hope.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hope.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "hope.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hope.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


Create a default fully qualified Elasticsearch name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.elasticsearch.fullname" -}}
{{- $name := default "elasticsearch" .Values.elasticsearch.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Get the Elasticsearch envs.
*/}}
{{- define "hope.elasticsearch.config" -}}
{{- if .Values.elasticsearch.enabled -}}
ELASTICSEARCH_HOST: {{ template "hope.elasticsearch.fullname" . }}-coordinating-only:9200
{{- else }}
ELASTICSEARCH_HOST: {{ .Values.externalElasticsearch.host }}
{{- end -}}
{{- end -}}

{{/*
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.postgresql.fullname" -}}
{{- $name := default "postgresql" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified registrationdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.registrationdatahubpostgresql.fullname" -}}
{{- $name := default "registrationdatahubpostgresql" .Values.registrationdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified cashassistdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.cashassistdatahubpostgresql.fullname" -}}
{{- $name := default "cashassistdatahubpostgresql" .Values.cashassistdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Get the Main PostgreSQL envs.
*/}}
{{- define "hope.postgresql.dburl" -}}
{{- if .Values.postgresql.ephemeral -}}
DATABASE_URL: {{ printf "postgis://%s:%s@%s:5432/%s" .Values.postgresql.username
    .Values.postgresql.auth.password
    (include "hope.postgresql.fullname" .)
    .Values.postgresql.auth.database | b64enc }}
{{- else }}
DATABASE_URL: {{ printf "postgis://%s:%s@%s:5432/%s"  .Values.postgresql.username
    .Values.postgresql.auth.password
    .Values.postgresql.auth.host
    .Values.postgresql.auth.database | b64enc }}
{{- end -}}
{{- end -}}

{{/*
Get the registrationdatahubpostgresql envs.
*/}}
{{- define "hope.registrationdatahubpostgresql.dburl" -}}
{{- if .Values.registrationdatahubpostgresql.ephemeral -}}
DATABASE_URL_HUB_REGISTRATION: {{ printf "postgis://%s:%s@%s:5432/%s"  .Values.registrationdatahubpostgresql.username
    .Values.registrationdatahubpostgresql.auth.password
    (include "hope.registrationdatahubpostgresql.fullname" .)
    .Values.registrationdatahubpostgresql.auth.database | b64enc }}
{{- else }}
DATABASE_URL_HUB_REGISTRATION: {{ printf "postgis://%s:%s@%s:5432/%s"  .Values.registrationdatahubpostgresql.username
    .Values.registrationdatahubpostgresql.auth.password
    .Values.registrationdatahubpostgresql.auth.host
    .Values.registrationdatahubpostgresql.auth.database | b64enc }}
{{- end -}}
{{- end -}}


{{/*
Get the cashassistdatahubpostgresql envs.
*/}}
{{- define "hope.cashassistdatahubpostgresql.dburl" -}}
{{- if .Values.cashassistdatahubpostgresql.ephemeral -}}
DATABASE_URL_HUB_MIS: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=mis"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    (include "hope.cashassistdatahubpostgresql.fullname" .)
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
DATABASE_URL_HUB_CA: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=ca"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    (include "hope.cashassistdatahubpostgresql.fullname" .)
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
DATABASE_URL_HUB_ERP: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=erp"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    (include "hope.cashassistdatahubpostgresql.fullname" .)
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
{{- else }}
DATABASE_URL_HUB_MIS: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=mis"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    .Values.cashassistdatahubpostgresql.auth.host
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
DATABASE_URL_HUB_CA: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=ca"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    .Values.cashassistdatahubpostgresql.auth.host
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
DATABASE_URL_HUB_ERP: {{ printf "postgis://%s:%s@%s:5432/%s?options=-c search_path=erp"  .Values.cashassistdatahubpostgresql.username
    .Values.cashassistdatahubpostgresql.auth.password
    .Values.cashassistdatahubpostgresql.auth.host
    .Values.cashassistdatahubpostgresql.auth.database | b64enc }}
{{- end -}}
{{- end -}}
