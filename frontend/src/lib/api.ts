import type {
  AuthSession,
  Expense,
  ExpenseCreate,
  Group,
  GroupInvite,
  GroupMessage,
  GuestAuthSession,
  InvitePreview,
  Participant,
  SettlementSummary
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
export const API_ORIGIN = API_BASE_URL.startsWith("http")
  ? API_BASE_URL.replace(/\/api\/v1\/?$/, "")
  : window.location.origin;
export const WS_BASE_URL = API_ORIGIN.replace(/^http/, "ws");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { headers, ...restOptions } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...headers
    }
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(typeof detail.detail === "string" ? detail.detail : "Request failed");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  signup: (email: string, password: string, displayName: string, settlementContact: string) =>
    request<AuthSession>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        display_name: displayName,
        settlement_contact: settlementContact
      })
    }),
  login: (email: string, password: string) =>
    request<AuthSession>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: (token: string) =>
    request<AuthSession["admin"]>("/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    }),
  guestMe: (token: string) =>
    request<GuestAuthSession>("/auth/guest/me", {
      headers: { Authorization: `Bearer ${token}` }
    }),
  logout: (token: string) =>
    request<void>("/auth/session", {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }),
  listGroups: (token: string) =>
    request<Group[]>("/groups", {
      headers: { Authorization: `Bearer ${token}` }
    }),
  createGroup: (name: string, currency: string, settlementContact: string, token: string) =>
    request<Group>("/groups", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name, currency, settlement_contact: settlementContact })
    }),
  updateGroup: (groupId: string, name: string, settlementContact: string, token: string) =>
    request<Group>(`/groups/${groupId}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name, settlement_contact: settlementContact })
    }),
  getGroup: (groupId: string, token: string) => request<Group>(`/groups/${groupId}`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  deleteGroup: (groupId: string, token: string) =>
    request<void>(`/groups/${groupId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }),
  addParticipant: (groupId: string, name: string, token: string) =>
    request<Participant>(`/groups/${groupId}/participants`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ name })
    }),
  createInvite: (groupId: string, token: string) =>
    request<GroupInvite>(`/groups/${groupId}/invites`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    }),
  getInvite: (token: string) => request<InvitePreview>(`/groups/invites/${token}`),
  joinInvite: (token: string, name: string) =>
    request<GuestAuthSession>(`/groups/invites/${token}/join`, {
      method: "POST",
      body: JSON.stringify({ name })
    }),
  listMessages: (groupId: string, token: string) => request<GroupMessage[]>(`/groups/${groupId}/messages`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  createMessage: (groupId: string, body: string, token: string) =>
    request<GroupMessage>(`/groups/${groupId}/messages`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ body })
    }),
  removeParticipant: (groupId: string, participantId: string, token: string) =>
    request<void>(`/groups/${groupId}/participants/${participantId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    }),
  addExpense: (groupId: string, payload: ExpenseCreate, token: string) =>
    request<Expense>(`/groups/${groupId}/expenses`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload)
    }),
  listExpenses: (groupId: string, token: string) => request<Expense[]>(`/groups/${groupId}/expenses`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  getSettlements: (groupId: string, token: string) => request<SettlementSummary>(`/groups/${groupId}/settlements`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  uploadGroupImage: (groupId: string, image: File, token: string) => {
    const form = new FormData();
    form.append("image", image);
    return fetch(`${API_BASE_URL}/groups/${groupId}/image`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form
    }).then(async (response) => {
      if (!response.ok) {
        const detail = await response.json().catch(() => ({ detail: "Image upload failed" }));
        throw new Error(typeof detail.detail === "string" ? detail.detail : "Image upload failed");
      }
      return response.json() as Promise<Group>;
    });
  }
};
