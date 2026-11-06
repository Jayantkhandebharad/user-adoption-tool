import { type FormEvent, type ReactNode, useState } from "react";
import { ApiError } from "../api";

interface Props {
  title: string;
  intro?: ReactNode;
  submitLabel: string;
  children: ReactNode;
  onSubmit: (form: FormData) => Promise<void>;
}

/** Shared card layout and submit/error handling for the setup and sign-in screens. */
export function AuthForm({ title, intro, submitLabel, children, onSubmit }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSubmit(new FormData(event.currentTarget));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
      setBusy(false);
    }
  }

  return (
    <main className="centered">
      <form className="card" onSubmit={handleSubmit}>
        <h1>{title}</h1>
        {intro}
        {children}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={busy}>
          {submitLabel}
        </button>
      </form>
    </main>
  );
}

export function field(form: FormData, name: string): string {
  return String(form.get(name) ?? "");
}
