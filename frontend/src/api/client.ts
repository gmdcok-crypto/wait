const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export type TicketStatus =
  | "waiting"
  | "called"
  | "completed"
  | "no_show"
  | "cancelled";

export interface Ticket {
  id: number;
  store_id: number;
  number: number;
  phone: string;
  party_size: number;
  status: TicketStatus;
  service_date: string;
  created_at: string;
  called_at: string | null;
  completed_at: string | null;
}

export interface TicketCallOut {
  ticket: Ticket;
  channel: string;
  message: string;
  success: boolean;
}

export interface Store {
  id: number;
  name: string;
  slug: string;
  created_at: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "요청 실패");
  }
  return res.json() as Promise<T>;
}

export function getStore(slug: string) {
  return request<Store>(`/api/stores/${slug}`);
}

export function registerTicket(phone: string, partySize: number, storeSlug: string) {
  return request<TicketCallOut>("/api/tickets", {
    method: "POST",
    body: JSON.stringify({
      store_slug: storeSlug,
      phone,
      party_size: partySize,
    }),
  });
}

export function listTickets(storeSlug: string, status?: TicketStatus) {
  const qs = new URLSearchParams({ store_slug: storeSlug, today_only: "true" });
  if (status) qs.set("status", status);
  return request<Ticket[]>(`/api/tickets?${qs}`);
}

export function callTicket(ticketId: number, recall = false) {
  const qs = recall ? "?recall=true" : "";
  return request<TicketCallOut>(`/api/tickets/${ticketId}/call${qs}`, {
    method: "POST",
  });
}

export function updateTicketStatus(ticketId: number, status: TicketStatus) {
  return request<Ticket>(`/api/tickets/${ticketId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}
