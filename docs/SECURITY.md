# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Report it privately through GitHub:
[**Report a vulnerability**](https://github.com/Jayantkhandebharad/user-adoption-tool/security/advisories/new).
If that is not possible, email jntkhandebharad@gmail.com with "SECURITY" in the subject.

Include what is affected (SDK, Studio, backend, a deployment file), steps to reproduce or a
proof of concept, the impact you see, and the version or commit.

## What to expect

- Acknowledgement within 3 working days.
- An assessment and a planned fix date within 10 working days.
- A fix released with a GitHub security advisory, crediting you unless you prefer otherwise.

Please give us a reasonable time to release a fix before disclosing publicly.

## Supported versions

Until 1.0, only the latest release receives security fixes. Self-hosters should upgrade to the
latest release to get them.

## Scope notes for self-hosters

Each instance is run by its own operator, who is responsible for TLS, database access, backups
and keeping the instance updated. Turn on identity verification (`userHash`) in production so
end users cannot impersonate each other through the SDK API.
