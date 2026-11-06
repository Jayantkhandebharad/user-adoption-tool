import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const ADA = { id: "1", email: "ada@example.com", name: "Ada", role: "admin" };

type Route = (body: unknown) => [status: number, json?: unknown];

/** Stub fetch with a map of "METHOD /path" -> handler, recording request bodies. */
function mockApi(routes: Record<string, Route>) {
  const calls: { key: string; body: unknown }[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init?: RequestInit) => {
      const key = `${init?.method ?? "GET"} ${path}`;
      const body = init?.body ? JSON.parse(String(init.body)) : undefined;
      calls.push({ key, body });
      const route = routes[key];
      if (!route) throw new TypeError(`unexpected request ${key}`);
      const [status, json] = route(body);
      return new Response(json === undefined ? null : JSON.stringify(json), { status });
    }),
  );
  return calls;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("creates the first admin on a fresh instance", async () => {
    const calls = mockApi({
      "GET /api/setup/status": () => [200, { needs_setup: true, token_required: false }],
      "POST /api/setup": () => [201, ADA],
    });
    const user = userEvent.setup();
    render(<App />);

    await user.type(await screen.findByLabelText("Name"), "Ada");
    await user.type(screen.getByLabelText("Email"), "ada@example.com");
    await user.type(screen.getByLabelText(/^Password/), "correct horse battery");
    await user.click(screen.getByRole("button", { name: "Create admin account" }));

    expect(await screen.findByRole("heading", { name: "Experiences" })).toBeInTheDocument();
    expect(calls.find((c) => c.key === "POST /api/setup")?.body).toEqual({
      name: "Ada",
      email: "ada@example.com",
      password: "correct horse battery",
    });
  });

  it("asks for the setup token when the instance requires one", async () => {
    mockApi({
      "GET /api/setup/status": () => [200, { needs_setup: true, token_required: true }],
    });
    render(<App />);
    expect(await screen.findByLabelText(/Setup token/)).toBeInTheDocument();
  });

  it("shows the server's error, then signs in", async () => {
    let attempts = 0;
    mockApi({
      "GET /api/setup/status": () => [200, { needs_setup: false, token_required: false }],
      "GET /api/auth/me": () => [401, { detail: "Not signed in" }],
      "POST /api/auth/login": () =>
        ++attempts === 1 ? [401, { detail: "Wrong email or password" }] : [200, ADA],
    });
    const user = userEvent.setup();
    render(<App />);

    await user.type(await screen.findByLabelText("Email"), "ada@example.com");
    await user.type(screen.getByLabelText("Password"), "nope");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Wrong email or password");

    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByText("Ada · admin")).toBeInTheDocument();
  });

  it("signs out", async () => {
    mockApi({
      "GET /api/setup/status": () => [200, { needs_setup: false, token_required: false }],
      "GET /api/auth/me": () => [200, ADA],
      "POST /api/auth/logout": () => [204],
    });
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Sign out" }));
    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  });

  it("explains when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Cannot reach the server");
  });
});
