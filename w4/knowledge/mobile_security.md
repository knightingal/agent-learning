# Mobile security review checklist

Do not include credentials or enrollment tokens in source code, logs, reports, or tests. Minimize collected data. Avoid network call in unit tests. Keep filesystem writes inside the configured workspace. Require approval before file writes or command execution with side effects.