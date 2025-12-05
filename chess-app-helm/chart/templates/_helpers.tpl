{{- define "chess.backendName" -}}
{{ include "chess.fullname" . }}-backend
{{- end }}

{{- define "chess.workerName" -}}
{{ include "chess.fullname" . }}-worker
{{- end }}

{{- define "chess.frontendName" -}}
{{ include "chess.fullname" . }}-frontend
{{- end }}

{{- define "chess.fullname" -}}
{{ .Chart.Name }}
{{- end }}
