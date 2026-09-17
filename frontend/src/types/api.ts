export type Participant = {
  id: string;
  group_id: string;
  name: string;
  is_active: boolean;
  created_at: string;
};

export type AdminUser = {
  id: string;
  email: string;
  display_name: string;
  settlement_contact: string;
  created_at: string;
};

export type AuthSession = {
  token: string;
  admin: AdminUser;
};

export type Group = {
  id: string;
  name: string;
  currency: string;
  admin_id: string | null;
  settlement_contact: string;
  image_url: string | null;
  owner_participant_id: string | null;
  created_at: string;
  participants: Participant[];
};

export type GroupInvite = {
  id: string;
  group_id: string;
  token: string;
  created_at: string;
};

export type InvitePreview = {
  token: string;
  group: Pick<Group, "id" | "name" | "currency" | "image_url">;
};

export type GuestAuthSession = {
  token: string;
  group_id: string;
  participant: Participant;
};

export type GroupMessage = {
  id: string;
  group_id: string;
  sender_name: string;
  body: string;
  created_at: string;
};

export type ExpenseParticipant = {
  participant: Participant;
  share: string;
};

export type Expense = {
  id: string;
  group_id: string;
  name: string;
  category: string;
  payer: Participant;
  subtotal: string;
  tax: string;
  tip: string;
  fees: string;
  discounts: string;
  total: string;
  currency: string;
  split_method: string;
  source: string;
  created_at: string;
  participants: ExpenseParticipant[];
};

export type ParticipantBalance = {
  participant_id: string;
  name: string;
  balance: string;
  currency: string;
};

export type Settlement = {
  from_participant_id: string;
  from_name: string;
  to_participant_id: string;
  to_name: string;
  amount: string;
  currency: string;
};

export type SettlementSummary = {
  balances: ParticipantBalance[];
  settlements: Settlement[];
};

export type ExpenseCreate = {
  name: string;
  category: string;
  payer_id: string;
  participant_ids: string[];
  subtotal: string;
  tax_rate: string;
  tax_amount?: string | null;
  tip_rate: string;
  tip_amount?: string | null;
  fees: string;
  discounts: string;
};
