import { useCallback, useEffect, useState } from "react";
import { ApiError, api, type Member, type SetupStatus } from "./api";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { SetupPage } from "./pages/SetupPage";

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "setup"; status: SetupStatus }
  | { kind: "signed-out" }
  | { kind: "signed-in"; member: Member };

/** Decides which screen to show: first-run setup, sign-in, or the app. */
export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  const load = useCallback(async () => {
    try {
      const status = await api.setupStatus();
      if (status.needs_setup) {
        setState({ kind: "setup", status });
        return;
      }
      setState({ kind: "signed-in", member: await api.me() });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setState({ kind: "signed-out" });
      } else {
        setState({ kind: "error", message: "Cannot reach the server. Is the backend running?" });
      }
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const signedIn = (member: Member) => setState({ kind: "signed-in", member });

  switch (state.kind) {
    case "loading":
      return null;
    case "error":
      return (
        <main className="centered">
          <p role="alert">{state.message}</p>
        </main>
      );
    case "setup":
      return <SetupPage tokenRequired={state.status.token_required} onDone={signedIn} />;
    case "signed-out":
      return <LoginPage onDone={signedIn} />;
    case "signed-in":
      return (
        <HomePage member={state.member} onSignedOut={() => setState({ kind: "signed-out" })} />
      );
  }
}
