# shared

Contracts used by more than one part. Change them here, never in a consumer.

- [`schema/`](schema/) — JSON Schemas for experience content (Flows, steps, buttons) and
  targeting rules. The backend validates against them; TypeScript types for the SDK and Studio
  are generated from them.
