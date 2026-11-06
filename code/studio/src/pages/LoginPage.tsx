import { api, type Member } from "../api";
import { AuthForm, field } from "./AuthForm";

export function LoginPage({ onDone }: { onDone: (member: Member) => void }) {
  return (
    <AuthForm
      title="Sign in"
      submitLabel="Sign in"
      onSubmit={async (form) => {
        onDone(await api.login({ email: field(form, "email"), password: field(form, "password") }));
      }}
    >
      <label>
        Email
        <input name="email" type="email" autoComplete="email" required />
      </label>
      <label>
        Password
        <input name="password" type="password" autoComplete="current-password" required />
      </label>
    </AuthForm>
  );
}
