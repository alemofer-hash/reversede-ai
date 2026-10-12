# Security policy

## Supported state

Reversede `0.3.0.dev0` is a private local development candidate. No public
release or public support window exists.

## Reporting

Report a suspected vulnerability privately to the project owner through the
private collaboration channel chosen by the user. Do not place secrets,
personal data, exploit payloads, or unredacted datasets in an issue or log.

A report should include the affected version, minimal reproduction, impact,
and whether generated blueprint source is involved. Secret values must be
redacted. No public disclosure should occur without the user's separate
authorization.

## Security boundaries

- Reversede analyzes data supplied by the caller; data governance remains with
  the caller.
- Generated blueprints are source code and must be reviewed before execution.
- Column names are emitted using Python literals, and alert text is rendered as
  comments; regression tests cover newline-based source injection.
- Optional integrations are lazy imports and are not required by the core.
- Reports may reveal schema and statistical properties and should be handled as
  potentially sensitive artifacts.
