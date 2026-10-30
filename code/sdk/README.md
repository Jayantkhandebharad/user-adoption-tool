# sdk

Browser SDK (TypeScript, no runtime dependencies, rendered inside a Shadow DOM root).

```html
<script src="https://guide.example.com/sdk.js"></script>
<script>Guide.init({ apiUrl: "https://guide.example.com" });</script>
```

Public API: `init`, `identify`, `group`, `track`, `page`, `show`, `reset`, `debug`, `on/off`.
Size budget: under 30 KB gzipped. Setup and commands are added here in milestone M1.
