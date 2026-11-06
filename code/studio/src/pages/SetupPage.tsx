import { api, type Member } from "../api";
import { AuthForm, field } from "./AuthForm";

const MIN_PASSWORD_LENGTH = 12;

interface Props {
  tokenRequired: boolean;
  onDone: (member: Member) => void;
}

export function SetupPage({ tokenRequired, onDone }: Props) {
  return (
    <AuthForm
      title="Set up your instance"
      intro={<p>Create the first admin account. You can invite your team afterwards.</p>}
      submitLabel="Create admin account"
      onSubmit={async (form) => {
        const member = await api.setup({
          name: field(form, "name"),
          email: field(form, "email"),
          password: field(form, "password"),
          ...(tokenRequired ? { setup_token: field(form, "setup_token") } : {}),
        });
        onDone(member);
      }}
    >
      <label>
        Name
        <input name="name" autoComplete="name" required />
      </label>
      <label>
        Email
        <input name="email" type="email" autoComplete="email" required />
      </label>
      <label>
        Password
        <input
          name="password"
          type="password"
          autoComplete="new-password"
          minLength={MIN_PASSWORD_LENGTH}
          required
        />
        <small>At least {MIN_PASSWORD_LENGTH} characters.</small>
      </label>
      {tokenRequired && (
        <label>
          Setup token
          <input name="setup_token" autoComplete="off" required />
          <small>The SETUP_TOKEN value from your instance's configuration.</small>
        </label>
      )}
    </AuthForm>
  );
}
