import { FormEvent, KeyboardEvent, ReactNode, useEffect, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  CalendarDays,
  Check,
  Code2,
  Copy,
  FileText,
  ImagePlus,
  Link2,
  LogOut,
  Mail,
  MessageCircle,
  Plus,
  ReceiptText,
  Send,
  Settings,
  Share2,
  Trash2,
  WalletCards,
  X,
} from "lucide-react";

import { API_ORIGIN, WS_BASE_URL, api } from "./lib/api";
import type { AdminUser, Expense, ExpenseCreate, Group, GroupMessage, GuestAuthSession, InvitePreview, SettlementSummary } from "./types/api";

const categories = ["Restaurant", "Groceries", "Transportation", "Accommodation", "Entertainment", "Shopping", "Utilities", "Tickets", "Other"];
const taxPresets = [
  { label: "Custom", value: "" },
  { label: "Ontario HST 13%", value: "13" },
  { label: "Alberta GST 5%", value: "5" },
  { label: "No tax", value: "0" }
];

function GithubIcon({ size = 16 }: { size?: number }) {
  return (
    <svg aria-hidden="true" height={size} viewBox="0 0 24 24" width={size} fill="currentColor">
      <path d="M12 .7a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2.23c-3.22.7-3.9-1.37-3.9-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.73-1.55-2.57-.29-5.27-1.28-5.27-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.16 1.18A10.98 10.98 0 0 1 12 6.12c.98 0 1.95.13 2.87.39 2.2-1.49 3.16-1.18 3.16-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.71 5.38-5.29 5.67.42.36.79 1.07.79 2.16v3.25c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .7Z" />
    </svg>
  );
}

function LinkedinIcon({ size = 16 }: { size?: number }) {
  return (
    <svg aria-hidden="true" height={size} viewBox="0 0 24 24" width={size} fill="currentColor">
      <path d="M5.37 7.98H1.81V19.4h3.56V7.98ZM3.59 2.3a2.06 2.06 0 1 0 0 4.12 2.06 2.06 0 0 0 0-4.12ZM19.7 13.54c0-3.44-1.84-5.04-4.29-5.04-1.98 0-2.86 1.09-3.35 1.85V7.98H8.5V19.4h3.56v-5.66c0-1.49.28-2.93 2.13-2.93 1.82 0 1.84 1.7 1.84 3.03v5.56h3.56l.11-5.86Z" />
    </svg>
  );
}

const portfolio = {
  name: "moaz aamir",
  role: "computer & software engineer",
  email: "moaz.aamir@torontomu.ca",
  links: [
    { label: "github", href: "https://github.com/moazaamir7", icon: GithubIcon },
    { label: "linkedin", href: "https://www.linkedin.com/in/moaza7/", icon: LinkedinIcon },
    { label: "resume", href: "/resume.pdf", icon: FileText },
    { label: "email", href: "mailto:moaz.aamir@torontomu.ca", icon: Mail }
  ],
  current: [
    {
      title: "Computer Engineering",
      org: "Toronto Metropolitan University",
      meta: "2024 - 2029",
      detail: "",
      href: "https://www.torontomu.ca/",
      logo: "/tmu-logo-one-colour.jpg"
    }
  ],
  previous: [
    {
      title: "SWE Intern",
      org: "Applied Optimal",
      meta: "May - Jul 2026",
      detail: "",
      skills: ["Flutter", "FastAPI", "Supabase", "RBAC", "Stripe"],
      href: "",
      logo: "/applied-optimal-logo.png"
    },
    {
      title: "SWE Intern",
      org: "Vision Allies",
      meta: "Mar - May 2026",
      detail: "",
      skills: ["TypeScript", "Material UI", "SaaS Architecture"],
      href: "https://vision-allies.com/",
      logo: "/vision-allies-enhanced.png"
    },
    {
      title: "SWE Intern",
      org: "0.5 Labs",
      meta: "Sep - Dec 2025",
      detail: "",
      skills: ["React.js", "Pandas", "SQL", "REST APIs"],
      href: "https://pointfivelabs.io/en",
      logo: "/pointfive.jpeg"
    },
    {
      title: "SWE Intern",
      org: "Stylus Marketing",
      meta: "May - Aug 2025",
      detail: "",
      skills: ["Python", "Excel", "Workflow Automation"],
      href: "https://www.stylusmarketing.ca/",
      logo: "/stylus-logo.png"
    }
  ],
  projects: [
    {
      title: "SettleSmart",
      stack: ["FastAPI", "PostgreSQL", "WebSockets"],
      href: "https://settlesmart-expenses.vercel.app",
      logo: "settlesmart"
    },
    {
      title: "Quoted.",
      stack: ["Python", "scikit-learn", "Explainable AI"],
      href: "https://github.com/moazaamir7/insurance-premium-ai",
      logo: "/quoted-logo.png"
    },
    {
      title: "MarketPilot AI",
      stack: ["React", "Chart.js", "SQLite", "Random Forest"],
      href: "https://github.com/moazaamir7/marketpilot-ai",
      logo: "/marketpilot-ai-logo.svg"
    }
  ]
};

const emptyExpense: ExpenseCreate = {
  name: "",
  category: "Restaurant",
  payer_id: "",
  participant_ids: [],
  subtotal: "",
  tax_rate: "13",
  tax_amount: null,
  tip_rate: "18",
  tip_amount: null,
  fees: "0",
  discounts: "0"
};

type AdminSession = {
  mode: "admin";
  token: string;
  admin: AdminUser;
};

type GuestSession = {
  mode: "guest";
  token: string;
  groupId: string;
  participantId: string;
  name: string;
};

type AppSession = AdminSession | GuestSession;
type AuthMode = "login" | "signup";

const sessionKey = "settlesmart-session";

function readStoredSession(): AppSession | null {
  try {
    const stored = window.localStorage.getItem(sessionKey);
    if (!stored) return null;
    const parsed = JSON.parse(stored) as Partial<AppSession>;
    if (parsed.mode === "admin" && parsed.token && parsed.admin) return parsed as AdminSession;
    if (parsed.mode === "guest" && parsed.token && parsed.groupId && parsed.participantId && parsed.name) return parsed as GuestSession;
    return null;
  } catch {
    return null;
  }
}

function money(value: string | number, currency = "CAD") {
  return new Intl.NumberFormat("en-CA", { style: "currency", currency }).format(Number(value));
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function validateExpense(expense: ExpenseCreate): string | null {
  if (!expense.name.trim()) return "Enter an expense name.";
  if (!expense.payer_id) return "Select who paid for the expense.";
  if (expense.participant_ids.length === 0) return "Select at least one participant.";

  const fields: Array<[string, string, boolean]> = [
    ["Subtotal", expense.subtotal, true],
    ["Tax percentage", expense.tax_rate, false],
    ["Tip percentage", expense.tip_rate, false],
    ["Fees", expense.fees, false],
    ["Discounts", expense.discounts, false]
  ];
  for (const [label, value, mustBePositive] of fields) {
    if (!/^\d+(\.\d{1,2})?$/.test(value) || !Number.isFinite(Number(value))) return `${label} must be a valid number with no more than two decimal places.`;
    if (mustBePositive && Number(value) <= 0) return "Subtotal must be greater than zero.";
  }
  if (Number(expense.tax_rate) > 100) return "Tax percentage cannot be greater than 100%.";
  if (Number(expense.tip_rate) > 100) return "Tip percentage cannot be greater than 100%.";
  const beforeDiscount = Number(expense.subtotal) * (1 + Number(expense.tax_rate) / 100 + Number(expense.tip_rate) / 100) + Number(expense.fees);
  if (Number(expense.discounts) > beforeDiscount) return "Discount cannot be greater than the expense total.";
  return null;
}

function preventInvalidNumberKey(event: KeyboardEvent<HTMLInputElement>) {
  if (["e", "E", "+", "-"].includes(event.key)) event.preventDefault();
}

function App() {
  const pathname = window.location.pathname;
  const [joinToken, setJoinToken] = useState(() => {
    const match = window.location.pathname.match(/^\/join\/([^/]+)$/);
    return match?.[1] ?? "";
  });
  const [session, setSession] = useState<AppSession | null>(() => readStoredSession());
  const [isSessionChecking, setIsSessionChecking] = useState(Boolean(session));
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [authForm, setAuthForm] = useState({ email: "", password: "", displayName: "", settlementContact: "" });
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState("");
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [messages, setMessages] = useState<GroupMessage[]>([]);
  const [summary, setSummary] = useState<SettlementSummary | null>(null);
  const [activeView, setActiveView] = useState<"overview" | "messages">("overview");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [currency, setCurrency] = useState("CAD");
  const [settlementContact, setSettlementContact] = useState("");
  const [settingsName, setSettingsName] = useState("");
  const [settingsContact, setSettingsContact] = useState("");
  const [participantName, setParticipantName] = useState("");
  const [expense, setExpense] = useState<ExpenseCreate>(emptyExpense);
  const [expenseError, setExpenseError] = useState<string | null>(null);
  const [inviteLink, setInviteLink] = useState("");
  const [inviteCopied, setInviteCopied] = useState(false);
  const [messageBody, setMessageBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const isAdmin = session?.mode === "admin";
  const currentName = session?.mode === "admin" ? session.admin.display_name : session?.name ?? "";
  const totalSpend = useMemo(() => expenses.reduce((sum, item) => sum + Number(item.total), 0), [expenses]);
  const myBalance = session?.mode === "guest"
    ? summary?.balances.find((balance) => balance.participant_id === session.participantId)
    : null;
  const mySettlements = session?.mode === "guest"
    ? summary?.settlements.filter(
        (settlement) =>
          settlement.from_participant_id === session.participantId ||
          settlement.to_participant_id === session.participantId
      )
    : [];

  function persistSession(nextSession: AppSession | null) {
    setSession(nextSession);
    if (nextSession) {
      window.localStorage.setItem(sessionKey, JSON.stringify(nextSession));
    } else {
      window.localStorage.removeItem(sessionKey);
    }
  }

  async function loadGroup(groupId: string, sessionOverride = session) {
    if (!sessionOverride) throw new Error("Authentication is required.");
    const [group, groupExpenses, settlements, groupMessages] = await Promise.all([
      api.getGroup(groupId, sessionOverride.token),
      api.listExpenses(groupId, sessionOverride.token),
      api.getSettlements(groupId, sessionOverride.token),
      api.listMessages(groupId, sessionOverride.token)
    ]);
    setSelectedGroupId(groupId);
    setSelectedGroup(group);
    setExpenses(groupExpenses);
    setSummary(settlements);
    setMessages(groupMessages);
    setSettingsName(group.name);
    setSettingsContact(group.settlement_contact);
    setExpense((current) => ({
      ...current,
      payer_id: current.payer_id || group.participants[0]?.id || "",
      participant_ids: current.participant_ids.length
        ? current.participant_ids.filter((id) => group.participants.some((participant) => participant.id === id))
        : group.participants.map((participant) => participant.id)
    }));
  }

  async function refresh(groupId = selectedGroupId, sessionOverride = session) {
    setError(null);
    if (!sessionOverride) return;
    if (sessionOverride.mode === "guest") {
      setGroups([]);
      await loadGroup(sessionOverride.groupId, sessionOverride);
      return;
    }
    const adminGroups = await api.listGroups(sessionOverride.token);
    setGroups(adminGroups);
    const activeId = adminGroups.some((group) => group.id === groupId) ? groupId : adminGroups[0]?.id || "";
    if (!activeId) {
      setSelectedGroupId("");
      setSelectedGroup(null);
      setExpenses([]);
      setMessages([]);
      setSummary(null);
      return;
    }
    await loadGroup(activeId, sessionOverride);
  }

  useEffect(() => {
    if (joinToken || pathname !== "/app" || !session) {
      setIsSessionChecking(false);
      return;
    }
    let cancelled = false;
    setIsSessionChecking(true);
    const validate = session.mode === "admin" ? api.me(session.token) : api.guestMe(session.token);
    validate
      .then(() => refresh("", session))
      .catch((caught) => {
        if (!cancelled) {
          persistSession(null);
          setError(caught instanceof Error ? caught.message : "Your session is no longer valid.");
        }
      })
      .finally(() => { if (!cancelled) setIsSessionChecking(false); });
    return () => { cancelled = true; };
  }, [joinToken, session?.token]);

  useEffect(() => {
    if (!session || !selectedGroupId || isSessionChecking) return;
    const socket = new WebSocket(`${WS_BASE_URL}/api/v1/groups/${selectedGroupId}/ws?token=${encodeURIComponent(session.token)}`);
    socket.onmessage = (event) => {
      const update = JSON.parse(event.data) as { type: string; message?: GroupMessage };
      if (update.type === "message.created" && update.message) {
        setMessages((current) => current.some((message) => message.id === update.message?.id) ? current : [...current, update.message as GroupMessage]);
      }
    };
    return () => socket.close();
  }, [session?.token, selectedGroupId, isSessionChecking]);

  async function handleAuth(event: FormEvent) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const response = authMode === "signup"
        ? await api.signup(authForm.email, authForm.password, authForm.displayName, authForm.settlementContact)
        : await api.login(authForm.email, authForm.password);
      const nextSession: AdminSession = { mode: "admin", token: response.token, admin: response.admin };
      persistSession(nextSession);
      setAuthForm({ email: "", password: "", displayName: "", settlementContact: "" });
      window.location.assign("/app");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not log in.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleLogout() {
    if (session) api.logout(session.token).catch(() => undefined);
    persistSession(null);
    setGroups([]);
    setSelectedGroupId("");
    setSelectedGroup(null);
    setExpenses([]);
    setMessages([]);
    setSummary(null);
    setActiveView("overview");
    setSettingsOpen(false);
    window.location.assign("/login");
  }

  async function handleGroupImage(image: File | undefined) {
    if (!image || !isAdmin || !selectedGroup) return;
    setIsLoading(true);
    setError(null);
    try {
      await api.uploadGroupImage(selectedGroup.id, image, session.token);
      await refresh(selectedGroup.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not upload the group image.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateGroup(event: FormEvent) {
    event.preventDefault();
    if (!isAdmin || !groupName.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const group = await api.createGroup(groupName.trim(), currency.trim().toUpperCase(), settlementContact.trim(), session.token);
      setGroupName("");
      setSettlementContact("");
      setSettingsOpen(false);
      await refresh(group.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not create group.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpdateGroup(event: FormEvent) {
    event.preventDefault();
    if (!isAdmin || !selectedGroup || !settingsName.trim()) return;
    setIsLoading(true);
    try {
      const group = await api.updateGroup(selectedGroup.id, settingsName.trim(), settingsContact.trim(), session.token);
      setSelectedGroup(group);
      await refresh(group.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not update group.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAddParticipant(event: FormEvent) {
    event.preventDefault();
    if (!isAdmin || !selectedGroup || !participantName.trim()) return;
    setIsLoading(true);
    try {
      await api.addParticipant(selectedGroup.id, participantName.trim(), session.token);
      setParticipantName("");
      await refresh(selectedGroup.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not add participant.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRemoveParticipant(participantId: string) {
    if (!isAdmin || !selectedGroup) return;
    setIsLoading(true);
    try {
      await api.removeParticipant(selectedGroup.id, participantId, session.token);
      await refresh(selectedGroup.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not remove participant.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDeleteGroup() {
    if (!isAdmin || !selectedGroup) return;
    const shouldDelete = window.confirm(`Delete "${selectedGroup.name}" and all temporary member data?`);
    if (!shouldDelete) return;
    setIsLoading(true);
    try {
      await api.deleteGroup(selectedGroup.id, session.token);
      setSettingsOpen(false);
      setInviteLink("");
      await refresh("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not delete group.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateInvite() {
    if (!isAdmin || !selectedGroup) return;
    setIsLoading(true);
    setInviteCopied(false);
    try {
      const invite = await api.createInvite(selectedGroup.id, session.token);
      setInviteLink(`${window.location.origin}/join/${invite.token}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not create invite link.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCopyInvite() {
    if (!inviteLink) return;
    await navigator.clipboard.writeText(inviteLink);
    setInviteCopied(true);
  }

  async function handleNativeShare() {
    if (!inviteLink || !selectedGroup) return;
    if (navigator.share) {
      await navigator.share({ title: `Join ${selectedGroup.name}`, text: `Join ${selectedGroup.name} on SettleSmart.`, url: inviteLink });
      return;
    }
    await handleCopyInvite();
  }

  async function handleAddExpense(event: FormEvent) {
    event.preventDefault();
    if (!isAdmin || !selectedGroup) return;
    const validationError = validateExpense(expense);
    if (validationError) {
      setExpenseError(validationError);
      return;
    }
    setIsLoading(true);
    setExpenseError(null);
    try {
      await api.addExpense(
        selectedGroup.id,
        {
          ...expense,
          subtotal: expense.subtotal || "0",
          tax_rate: expense.tax_rate || "0",
          tip_rate: expense.tip_rate || "0",
          fees: expense.fees || "0",
          discounts: expense.discounts || "0"
        },
        session.token
      );
      setExpense({
        ...emptyExpense,
        payer_id: selectedGroup.participants[0]?.id || "",
        participant_ids: selectedGroup.participants.map((participant) => participant.id)
      });
      setExpenseError(null);
      await refresh(selectedGroup.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not add expense.");
    } finally {
      setIsLoading(false);
    }
  }

  function toggleParticipant(participantId: string) {
    setExpense((current) => ({
      ...current,
      participant_ids: current.participant_ids.includes(participantId)
        ? current.participant_ids.filter((id) => id !== participantId)
        : [...current.participant_ids, participantId]
    }));
  }

  async function handleSendMessage(event: FormEvent) {
    event.preventDefault();
    if (!session || !selectedGroup || !currentName || !messageBody.trim()) return;
    setIsLoading(true);
    try {
      await api.createMessage(selectedGroup.id, messageBody.trim(), session.token);
      setMessageBody("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not send message.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleJoinedGroup(result: GuestAuthSession) {
    const nextSession: GuestSession = { mode: "guest", token: result.token, groupId: result.group_id, participantId: result.participant.id, name: result.participant.name };
    persistSession(nextSession);
    setJoinToken("");
    setActiveView("overview");
    window.location.assign("/app");
  }

  if (joinToken) {
    return <JoinInvite token={decodeURIComponent(joinToken)} onJoined={handleJoinedGroup} />;
  }

  if (pathname === "/") {
    return <LandingPage hasSession={Boolean(session)} />;
  }

  if (isSessionChecking) {
    return <main className="login-shell"><section className="session-loading"><span className="brand-mark large"><WalletCards size={34} /></span><p>Checking your session...</p></section></main>;
  }

  if (!session || pathname === "/login") {
    return (
      <main className="login-shell">
        <section className="login-panel">
          <span className="brand-mark large"><WalletCards size={34} /></span>
          <div>
            <p className="eyebrow">SettleSmart</p>
            <h1>{authMode === "signup" ? "Create your admin account" : "Log in as admin"}</h1>
            <p>{authMode === "signup" ? "Admins create groups, invite people, and close everything when the group is done." : "Invited members do not need accounts. They join through the invite link."}</p>
          </div>
          {error && <div className="error">{error}</div>}
          <form className="login-form" onSubmit={handleAuth}>
            {authMode === "signup" && (
              <>
                <label>
                  Name
                  <input value={authForm.displayName} onChange={(event) => setAuthForm({ ...authForm, displayName: event.target.value })} placeholder="Alex Morgan" />
                </label>
                <label>
                  E-transfer email or phone
                  <input value={authForm.settlementContact} onChange={(event) => setAuthForm({ ...authForm, settlementContact: event.target.value })} placeholder="alex@example.com or (000) 000-0000" />
                </label>
              </>
            )}
            <label>
              Email
              <input type="email" value={authForm.email} onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })} placeholder="name@example.com" autoFocus />
            </label>
            <label>
              Password
              <input type="password" value={authForm.password} onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })} placeholder="At least 10 characters" minLength={authMode === "signup" ? 10 : 1} />
            </label>
            <button type="submit" disabled={isLoading || !authForm.email.trim() || !authForm.password.trim()}>
              {authMode === "signup" ? "Create account" : "Log in"}
            </button>
          </form>
          <button className="text-action" type="button" onClick={() => setAuthMode(authMode === "signup" ? "login" : "signup")}>
            {authMode === "signup" ? "Already have an account? Log in" : "Need an admin account? Sign up"}
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="app-layout">
      <aside className="group-sidebar">
        <div className="sidebar-brand">
          <span className="brand-mark"><WalletCards size={21} /></span>
          <div>
            <h1>SettleSmart</h1>
            <p>{isAdmin ? session.admin.email : "Temporary member"}</p>
          </div>
        </div>

        {isAdmin && (
          <form className="sidebar-create" onSubmit={handleCreateGroup}>
            <label>
              New group
              <input value={groupName} onChange={(event) => setGroupName(event.target.value)} placeholder="Cottage Weekend" />
            </label>
            <label>
              E-transfer contact
              <input value={settlementContact} onChange={(event) => setSettlementContact(event.target.value)} placeholder={session.admin.settlement_contact || "email or phone"} />
            </label>
            <div className="row">
              <label>
                Currency
                <select value={currency} onChange={(event) => setCurrency(event.target.value)}>
                  <option value="CAD">CAD</option>
                  <option value="USD">USD</option>
                </select>
              </label>
              <button type="submit" disabled={isLoading || !groupName.trim()} title="Create group"><Plus size={18} /></button>
            </div>
          </form>
        )}

        <nav className="sidebar-groups" aria-label="Groups">
          {isAdmin ? groups.map((group) => (
            <button key={group.id} className={group.id === selectedGroupId ? "selected" : ""} onClick={() => refresh(group.id).catch((caught) => setError(caught.message))}>
              <span className="group-list-item">
                <span className="group-thumb">{group.image_url ? <img src={`${API_ORIGIN}${group.image_url}`} alt="" /> : initials(group.name)}</span>
                <span><strong>{group.name}</strong><small>{group.participants.length} {group.participants.length === 1 ? "member" : "members"}</small></span>
              </span>
            </button>
          )) : selectedGroup ? (
            <button className="selected">
              <span>{selectedGroup.name}</span>
              <small>Member view</small>
            </button>
          ) : null}
        </nav>

        <button type="button" className="ghost-action logout-action" onClick={handleLogout}>
          <LogOut size={17} />
          {isAdmin ? "Log out" : "Leave view"}
        </button>
      </aside>

      <section className="main-column">
        {error && <div className="error">{error}</div>}

        {selectedGroup ? (
          <>
            <header className="group-header">
              <div>
                <p className="eyebrow">{isAdmin ? "Admin overview" : "Group summary"}</p>
                <h2>{selectedGroup.name}</h2>
              </div>
              <div className="header-actions">
                <nav className="view-tabs" aria-label="Group sections">
                  <button type="button" className={activeView === "overview" ? "selected" : ""} onClick={() => setActiveView("overview")}>Overview</button>
                  <button type="button" className={activeView === "messages" ? "selected" : ""} onClick={() => setActiveView("messages")}><MessageCircle size={17} />Messages</button>
                </nav>
                {isAdmin && (
                  <button className="icon-button" type="button" onClick={() => setSettingsOpen((open) => !open)} title="Group settings">
                    <Settings size={19} />
                  </button>
                )}
              </div>
            </header>

            {isAdmin && settingsOpen && (
              <section className="panel settings-panel">
                <div className="panel-title"><Settings size={20} /><h3>Group settings</h3></div>
                <form className="settings-grid" onSubmit={handleUpdateGroup}>
                  <label>
                    Group name
                    <input value={settingsName} onChange={(event) => setSettingsName(event.target.value)} />
                  </label>
                  <label>
                    Admin e-transfer contact
                    <input value={settingsContact} onChange={(event) => setSettingsContact(event.target.value)} placeholder="email or phone" />
                  </label>
                  <button type="submit" disabled={isLoading || !settingsName.trim()}>Save settings</button>
                </form>
                <label className="image-upload-control">
                  <span className="group-thumb large">{selectedGroup.image_url ? <img src={`${API_ORIGIN}${selectedGroup.image_url}`} alt="Group" /> : initials(selectedGroup.name)}</span>
                  <span><strong>Group image</strong><small>JPG, PNG, or WebP up to 5 MB</small></span>
                  <span className="upload-button"><ImagePlus size={17} />Choose image</span>
                  <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => handleGroupImage(event.target.files?.[0])} disabled={isLoading} />
                </label>
                <div className="settings-grid settings-actions-grid">
                  <div className="invite-box">
                    <button type="button" onClick={handleCreateInvite} disabled={isLoading}><Link2 size={18} />Create invite link</button>
                    {inviteLink && (
                      <>
                        <input readOnly value={inviteLink} aria-label="Shareable invite link" />
                        <div className="invite-actions">
                          <button type="button" onClick={handleCopyInvite}>{inviteCopied ? <Check size={18} /> : <Copy size={18} />}{inviteCopied ? "Copied" : "Copy"}</button>
                          <button type="button" onClick={handleNativeShare}><Share2 size={18} />Share</button>
                        </div>
                      </>
                    )}
                  </div>
                  <form className="inline-form" onSubmit={handleAddParticipant}>
                    <input value={participantName} onChange={(event) => setParticipantName(event.target.value)} placeholder="Add a member" />
                    <button type="submit" disabled={isLoading || !participantName.trim()}><Plus size={18} /></button>
                  </form>
                </div>
                <div className="people-list">
                  {selectedGroup.participants.map((participant) => (
                    <div key={participant.id} className="person-row">
                      <span className="person-identity"><span className="avatar">{initials(participant.name)}</span>{participant.name}</span>
                      {participant.id === selectedGroup.owner_participant_id ? <span className="owner-badge">Admin</span> : <button onClick={() => handleRemoveParticipant(participant.id)} title="Remove member"><Trash2 size={16} /></button>}
                    </div>
                  ))}
                </div>
                <button className="danger-action standalone-danger" type="button" onClick={handleDeleteGroup} disabled={isLoading}>
                  <Trash2 size={17} />
                  Delete group
                </button>
              </section>
            )}

            {activeView === "messages" ? (
              <MessagesPanel messages={messages} messageBody={messageBody} setMessageBody={setMessageBody} onSend={handleSendMessage} isLoading={isLoading} senderName={currentName} />
            ) : isAdmin ? (
              <AdminOverview
                selectedGroup={selectedGroup}
                expenses={expenses}
                summary={summary}
                totalSpend={totalSpend}
                expense={expense}
                setExpense={setExpense}
                toggleParticipant={toggleParticipant}
                handleAddExpense={handleAddExpense}
                expenseError={expenseError}
                isLoading={isLoading}
              />
            ) : (
              <MemberOverview
                selectedGroup={selectedGroup}
                expenses={expenses}
                summary={summary}
                myBalance={myBalance}
                mySettlements={mySettlements ?? []}
              />
            )}
          </>
        ) : (
          <section className="empty-state dashboard-empty">
            <span className="brand-mark large"><WalletCards size={34} /></span>
            <h2>Create your first group</h2>
            <p>Use the form in the sidebar. You will be the admin, and invited people will get a simpler temporary view.</p>
          </section>
        )}
      </section>
    </main>
  );
}

function LandingPage({ hasSession: _hasSession }: { hasSession: boolean }) {
  const [resumeOpen, setResumeOpen] = useState(false);
  const [moreProjectsOpen, setMoreProjectsOpen] = useState(false);

  useEffect(() => {
    if (!resumeOpen) return;

    const previousOverflow = document.body.style.overflow;
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") setResumeOpen(false);
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", closeOnEscape);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", closeOnEscape);
    };
  }, [resumeOpen]);

  return (
    <main className="portfolio-page">
      <section className="portfolio-shell">
        <header className="portfolio-hero">
          <div className="portfolio-title">
            <p>{portfolio.role}</p>
            <h1>{portfolio.name}</h1>
            <nav className="portfolio-nav" aria-label="Primary links">
              {portfolio.links.map(({ label, href, icon: Icon }) =>
                label === "resume" ? (
                  <button aria-label="preview resume" key={label} onClick={() => setResumeOpen(true)} title="resume" type="button">
                    <Icon size={17} />
                  </button>
                ) : (
                  <a
                    aria-label={label}
                    href={href}
                    key={label}
                    rel="noreferrer"
                    target={href.startsWith("http") ? "_blank" : undefined}
                    title={label}
                  >
                    <Icon size={17} />
                  </a>
                )
              )}
            </nav>
          </div>

        </header>

        <PortfolioSection icon={<BriefcaseBusiness size={18} />} title="currently" items={portfolio.current} />
        <PortfolioSection icon={<CalendarDays size={18} />} title="previously" items={portfolio.previous} />

        <section className="portfolio-section" aria-labelledby="projects-heading">
          <div className="portfolio-section-title">
            <Code2 size={18} />
            <h2 id="projects-heading">projects</h2>
          </div>
          <div className="portfolio-list">
            {portfolio.projects.map((project) => (
              <a className="portfolio-item project-item" key={project.title} href={project.href} target="_blank" rel="noreferrer">
                <span className="project-heading">
                  {project.logo === "settlesmart" ? (
                    <span className="project-logo" aria-hidden="true"><WalletCards size={20} /></span>
                  ) : project.logo ? (
                    <img className="project-image-logo" src={project.logo} alt="" aria-hidden="true" />
                  ) : null}
                  <span className="item-main">
                    <strong>{project.title}</strong>
                  </span>
                </span>
                <span className="tech-list">{project.stack.map((tech) => <small key={tech}>{tech}</small>)}</span>
              </a>
            ))}
          </div>
          <button
            aria-controls="more-projects"
            aria-expanded={moreProjectsOpen}
            className="projects-more-button"
            onClick={() => setMoreProjectsOpen((open) => !open)}
            type="button"
          >
            {moreProjectsOpen ? "- see less" : "+ see more"}
          </button>
          <div className="portfolio-list more-projects" hidden={!moreProjectsOpen} id="more-projects" />
        </section>

        <footer className="portfolio-footer">
          <span>last updated: september 2026</span>
          <a href={`mailto:${portfolio.email}`}>{portfolio.email}</a>
        </footer>
      </section>

      {resumeOpen && (
        <div className="resume-preview-backdrop" role="presentation" onClick={() => setResumeOpen(false)}>
          <section className="resume-preview" role="dialog" aria-modal="true" aria-labelledby="resume-preview-title" onClick={(event) => event.stopPropagation()}>
            <header>
              <span id="resume-preview-title">resume.pdf</span>
              <button aria-label="close resume preview" onClick={() => setResumeOpen(false)} title="close" type="button">
                <X size={17} />
              </button>
            </header>
            <div className="resume-page-scroll">
              <img src="/resume-pages/moaz-aamir-resume.png" alt="Moaz Aamir resume" />
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

function PortfolioSection({
  icon,
  title,
  items
}: {
  icon: ReactNode;
  title: string;
  items: Array<{ title: string; org: string; meta: string; detail: string; href: string; logo?: string; skills?: string[] }>;
}) {
  return (
    <section className="portfolio-section" aria-labelledby={`${title}-heading`}>
      <div className="portfolio-section-title">
        {icon}
        <h2 id={`${title}-heading`}>{title}</h2>
      </div>
      <div className="portfolio-list">
        {items.map((item) => {
          const content = (
            <>
              {item.logo && <img className="item-logo" src={item.logo} alt={item.org} />}
              <span className="item-main">
                <strong>{item.title}</strong>
                <small>{item.org}</small>
              </span>
              {item.detail && <span className="item-detail">{item.detail}</span>}
              <span className="item-meta">{item.meta}</span>
              {item.skills && (
                <span className="tech-list experience-skills">
                  {item.skills.map((skill) => <small key={skill}>{skill}</small>)}
                </span>
              )}
            </>
          );

          return item.href ? (
            <a className={`portfolio-item${item.skills ? " experience-item" : ""}${item.logo ? " logo-item" : ""}${item.skills && item.logo ? " experience-logo-item" : ""}`} key={`${item.title}-${item.org}`} href={item.href} target="_blank" rel="noreferrer">
              {content}
            </a>
          ) : (
            <article className={`portfolio-item portfolio-item-static${item.skills ? " experience-item" : ""}`} key={`${item.title}-${item.org}`}>
              {content}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function AdminOverview({
  selectedGroup,
  expenses,
  summary,
  totalSpend,
  expense,
  setExpense,
  toggleParticipant,
  handleAddExpense,
  expenseError,
  isLoading
}: {
  selectedGroup: Group;
  expenses: Expense[];
  summary: SettlementSummary | null;
  totalSpend: number;
  expense: ExpenseCreate;
  setExpense: (expense: ExpenseCreate) => void;
  toggleParticipant: (participantId: string) => void;
  handleAddExpense: (event: FormEvent) => Promise<void>;
  expenseError: string | null;
  isLoading: boolean;
}) {
  return (
    <div className="overview-stack">
      <section className="metric-strip">
        <span><strong>{selectedGroup.participants.length}</strong>{selectedGroup.participants.length === 1 ? "Member" : "Members"}</span>
        <span><strong>{expenses.length}</strong>{expenses.length === 1 ? "Expense" : "Expenses"}</span>
        <span><strong>{money(totalSpend, selectedGroup.currency)}</strong>Total spent</span>
        <span><strong>{summary?.settlements.length ?? 0}</strong>{summary?.settlements.length === 1 ? "Settlement" : "Settlements"}</span>
      </section>

      <section className="panel expense-form-panel" id="new-expense">
        <div className="panel-title"><ReceiptText size={20} /><h3>Add expense</h3></div>
        <form className="expense-form" onSubmit={handleAddExpense}>
          {expenseError && <div className="form-error" role="alert">{expenseError}</div>}
          <div className="form-grid">
            <label>Name<input value={expense.name} onChange={(event) => setExpense({ ...expense, name: event.target.value })} placeholder="Uber" required /></label>
            <label>Category<select value={expense.category} onChange={(event) => setExpense({ ...expense, category: event.target.value })}>{categories.map((category) => <option key={category}>{category}</option>)}</select></label>
            <label>Subtotal<input type="number" inputMode="decimal" min="0.01" step="0.01" value={expense.subtotal} onKeyDown={preventInvalidNumberKey} onChange={(event) => setExpense({ ...expense, subtotal: event.target.value })} required /></label>
            <label>Paid by<select value={expense.payer_id} onChange={(event) => setExpense({ ...expense, payer_id: event.target.value })} required><option value="">Select payer</option>{selectedGroup.participants.map((participant) => <option key={participant.id} value={participant.id}>{participant.name}</option>)}</select></label>
            <label>Tax preset<select value={taxPresets.some((preset) => preset.value === expense.tax_rate) ? expense.tax_rate : ""} onChange={(event) => setExpense({ ...expense, tax_rate: event.target.value })}>{taxPresets.map((preset) => <option key={preset.label} value={preset.value}>{preset.label}</option>)}</select></label>
            <label>Tax %<input type="number" inputMode="decimal" min="0" max="100" step="0.01" value={expense.tax_rate} onKeyDown={preventInvalidNumberKey} onChange={(event) => setExpense({ ...expense, tax_rate: event.target.value })} /></label>
            <label>Tip %<input type="number" inputMode="decimal" min="0" max="100" step="0.01" value={expense.tip_rate} onKeyDown={preventInvalidNumberKey} onChange={(event) => setExpense({ ...expense, tip_rate: event.target.value })} /></label>
            <label>Fees<input type="number" inputMode="decimal" min="0" step="0.01" value={expense.fees} onKeyDown={preventInvalidNumberKey} onChange={(event) => setExpense({ ...expense, fees: event.target.value })} /></label>
            <label>Discounts<input type="number" inputMode="decimal" min="0" step="0.01" value={expense.discounts} onKeyDown={preventInvalidNumberKey} onChange={(event) => setExpense({ ...expense, discounts: event.target.value })} /></label>
          </div>
          <div className="participant-picker">
            {selectedGroup.participants.map((participant) => (
              <label key={participant.id} className="check-pill">
                <input type="checkbox" checked={expense.participant_ids.includes(participant.id)} onChange={() => toggleParticipant(participant.id)} />
                {participant.name}
              </label>
            ))}
          </div>
          <button className="primary-action" type="submit" disabled={isLoading || selectedGroup.participants.length === 0}><Plus size={18} />Add equal split expense</button>
        </form>
      </section>

      <div className="content-grid bottom-grid">
        <BalancesPanel summary={summary} />
        <SettlementsPanel summary={summary} />
      </div>
      <ExpenseHistory expenses={expenses} currency={selectedGroup.currency} />
    </div>
  );
}

function MemberOverview({
  selectedGroup,
  expenses,
  summary,
  myBalance,
  mySettlements
}: {
  selectedGroup: Group;
  expenses: Expense[];
  summary: SettlementSummary | null;
  myBalance?: SettlementSummary["balances"][number] | null;
  mySettlements: SettlementSummary["settlements"];
}) {
  return (
    <div className="member-stack">
      <section className="member-hero panel">
        <div>
          <p className="eyebrow">Your part</p>
          <h3>{myBalance ? money(myBalance.balance, myBalance.currency) : money(0, selectedGroup.currency)}</h3>
          <p>{Number(myBalance?.balance ?? 0) < 0 ? "You owe money back to the group." : "You are covered or owed money."}</p>
        </div>
        <div className="contact-card">
          <span>Send e-transfer to</span>
          <strong>{selectedGroup.settlement_contact || "Ask the admin for their e-transfer contact."}</strong>
        </div>
      </section>

      <section className="panel">
        <h3>What to pay</h3>
        <div className="settlement-list">
          {mySettlements.length ? mySettlements.map((settlement) => (
            <div key={`${settlement.from_participant_id}-${settlement.to_participant_id}`} className="settlement-row">
              <span><strong>{settlement.from_name}</strong> pays <strong>{settlement.to_name}</strong></span>
              <strong>{money(settlement.amount, settlement.currency)}</strong>
            </div>
          )) : <p className="muted">No payment needed right now.</p>}
        </div>
      </section>

      <BalancesPanel summary={summary} />
      <ExpenseHistory expenses={expenses} currency={selectedGroup.currency} />
    </div>
  );
}

function BalancesPanel({ summary }: { summary: SettlementSummary | null }) {
  return (
    <section className="panel">
      <h3>Balances</h3>
      <div className="balance-list">
        {summary?.balances.map((balance) => (
          <div key={balance.participant_id} className="balance-row">
            <span className="person-identity"><span className="avatar subtle">{initials(balance.name)}</span>{balance.name}</span>
            <strong className={Number(balance.balance) >= 0 ? "positive" : "negative"}>{money(balance.balance, balance.currency)}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function SettlementsPanel({ summary }: { summary: SettlementSummary | null }) {
  return (
    <section className="panel">
      <h3>Optimized settlements</h3>
      <div className="settlement-list">
        {summary?.settlements.length ? summary.settlements.map((settlement) => (
          <div key={`${settlement.from_participant_id}-${settlement.to_participant_id}`} className="settlement-row">
            <span><strong>{settlement.from_name}</strong> pays <strong>{settlement.to_name}</strong></span>
            <strong>{money(settlement.amount, settlement.currency)}</strong>
          </div>
        )) : <p className="muted">No settlement payments needed.</p>}
      </div>
    </section>
  );
}

function ExpenseHistory({ expenses, currency }: { expenses: Expense[]; currency: string }) {
  return (
    <section className="panel">
      <h3>Expense history</h3>
      <div className="expense-list">
        {expenses.length ? expenses.map((item) => (
          <article key={item.id} className="expense-row">
            <div><strong>{item.name}</strong><span>{item.category} · paid by {item.payer.name}</span></div>
            <div><strong>{money(item.total, item.currency || currency)}</strong><span>{item.participants.length} participants</span></div>
          </article>
        )) : <p className="muted">No expenses yet.</p>}
      </div>
    </section>
  );
}

function MessagesPanel({
  messages,
  messageBody,
  setMessageBody,
  onSend,
  isLoading,
  senderName
}: {
  messages: GroupMessage[];
  messageBody: string;
  setMessageBody: (message: string) => void;
  onSend: (event: FormEvent) => Promise<void>;
  isLoading: boolean;
  senderName: string;
}) {
  return (
    <section className="panel messages-page">
      <div className="panel-title"><MessageCircle size={20} /><h3>Group messages</h3></div>
      <div className="message-list">
        {messages.length ? messages.map((message) => (
          <article key={message.id} className="message-row">
            <span className="avatar subtle">{initials(message.sender_name)}</span>
            <div><strong>{message.sender_name}</strong><p>{message.body}</p><small>{new Date(message.created_at).toLocaleString()}</small></div>
          </article>
        )) : <p className="muted">No messages yet.</p>}
      </div>
      <form className="message-form" onSubmit={onSend}>
        <label>Message<textarea value={messageBody} onChange={(event) => setMessageBody(event.target.value)} placeholder="Send a quick update..." rows={3} /></label>
        <button type="submit" disabled={isLoading || !messageBody.trim()}><Send size={18} />Send as {senderName}</button>
      </form>
    </section>
  );
}

function JoinInvite({ token, onJoined }: { token: string; onJoined: (result: GuestAuthSession) => Promise<void> }) {
  const [preview, setPreview] = useState<InvitePreview | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isJoining, setIsJoining] = useState(false);

  useEffect(() => {
    if (token === "{invite_token}" || token.includes("{") || token.includes("}")) {
      setError("That is the example link format. Ask the admin to send the generated invite link.");
      return;
    }
    api.getInvite(token)
      .then(setPreview)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Invite link not found."));
  }, [token]);

  async function handleJoin(event: FormEvent) {
    event.preventDefault();
    if (!preview || !name.trim()) return;
    setIsJoining(true);
    setError(null);
    try {
      const guestSession = await api.joinInvite(token, name.trim());
      await onJoined(guestSession);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not join group.");
    } finally {
      setIsJoining(false);
    }
  }

  return (
    <main className="join-shell">
      <section className="join-panel">
        <WalletCards size={36} />
        <div>
          <h1>{preview ? `Join ${preview.group.name}` : "Opening invite"}</h1>
          <p>{preview ? "Enter your name to see the simple group summary and messages." : "Checking the link..."}</p>
        </div>
        {error && <div className="error">{error}</div>}
        {preview && (
          <form className="join-form" onSubmit={handleJoin}>
            <label>Your name<input value={name} onChange={(event) => setName(event.target.value)} placeholder="Adam" autoFocus /></label>
            <button type="submit" disabled={isJoining || !name.trim()}><Plus size={18} />Join group</button>
          </form>
        )}
      </section>
    </main>
  );
}

export default App;
