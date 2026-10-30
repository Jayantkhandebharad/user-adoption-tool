# infra

Everything needed to run the tool, locally or in a cloud.

| Folder | What |
|---|---|
| [`docker/`](docker/) | Container image and Compose files: the self-host stack and the local development stack (emulators) |
| [`aws/`](aws/) | Reference deployment on AWS (infrastructure as code) |
| [`azure/`](azure/) | Reference deployment on Azure (infrastructure as code) |

The cloud folders are optional reference setups. The supported baseline is the Docker image
plus a Postgres database, which runs anywhere.
