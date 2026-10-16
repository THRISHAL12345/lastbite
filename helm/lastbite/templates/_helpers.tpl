{{- define "lastbite.name" -}}
{{- .Release.Name | trunc 40 | trimSuffix "-" -}}
{{- end -}}
{{- define "lastbite.dbEnv" -}}
- name: DB_HOST
  value: {{ include "lastbite.name" . }}-postgres
- name: DB_NAME
  value: {{ .Values.database.name | quote }}
- name: DB_USER
  value: {{ .Values.database.user | quote }}
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.database.existingSecret }}
      key: {{ .Values.database.passwordKey }}
{{- end -}}
