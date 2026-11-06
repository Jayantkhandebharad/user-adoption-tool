import { api, type Member } from "../api";

interface Props {
  member: Member;
  onSignedOut: () => void;
}

export function HomePage({ member, onSignedOut }: Props) {
  async function signOut() {
    await api.logout();
    onSignedOut();
  }

  return (
    <div className="shell">
      <header className="topbar">
        <strong>Studio</strong>
        <span className="spacer" />
        <span>
          {member.name} · {member.role}
        </span>
        <button type="button" className="secondary" onClick={signOut}>
          Sign out
        </button>
      </header>
      <main className="content">
        <h1>Experiences</h1>
        <p className="empty">No experiences yet. Building Flows arrives in a later milestone.</p>
      </main>
    </div>
  );
}
