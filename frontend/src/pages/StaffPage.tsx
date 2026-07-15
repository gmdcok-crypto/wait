import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  callTicket,
  listTickets,
  Ticket,
  updateTicketStatus,
} from "../api/client";

const STORE_SLUG = import.meta.env.VITE_STORE_SLUG || "demo";

export default function StaffPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listTickets(STORE_SLUG);
      setTickets(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "목록을 불러오지 못했습니다");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(id);
  }, [refresh]);

  async function onCall(ticket: Ticket, recall = false) {
    setBusyId(ticket.id);
    try {
      const out = await callTicket(ticket.id, recall);
      setToast(`${ticket.number}번 → ${out.channel}: ${out.message}`);
      await refresh();
    } catch (err) {
      setToast(err instanceof Error ? err.message : "호출 실패");
    } finally {
      setBusyId(null);
    }
  }

  async function onStatus(ticket: Ticket, status: "completed" | "no_show") {
    setBusyId(ticket.id);
    try {
      await updateTicketStatus(ticket.id, status);
      await refresh();
    } catch (err) {
      setToast(err instanceof Error ? err.message : "상태 변경 실패");
    } finally {
      setBusyId(null);
    }
  }

  const active = tickets.filter((t) => t.status === "waiting" || t.status === "called");
  const done = tickets.filter((t) => t.status === "completed" || t.status === "no_show");

  return (
    <main className="staff">
      <header className="staff-header">
        <div>
          <p className="eyebrow">호출 앱 · {STORE_SLUG}</p>
          <h1>오늘의 대기열</h1>
        </div>
        <button className="btn btn-secondary" type="button" onClick={() => void refresh()}>
          새로고침
        </button>
      </header>

      {toast && (
        <div className="toast" role="status">
          {toast}
          <button type="button" onClick={() => setToast(null)}>
            닫기
          </button>
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {loading && <p className="meta">불러오는 중…</p>}

      <section className="queue">
        <h2>대기 / 호출중</h2>
        {active.length === 0 && !loading && <p className="meta">대기 중인 고객이 없습니다.</p>}
        <ul className="ticket-list">
          {active.map((t) => (
            <li key={t.id} className={`ticket-row status-${t.status}`}>
              <div className="ticket-main">
                <span className="num">{t.number}</span>
                <div>
                  <strong>{maskPhone(t.phone)}</strong>
                  <p className="meta">
                    {t.party_size}명 · {statusLabel(t.status)}
                  </p>
                </div>
              </div>
              <div className="ticket-actions">
                <button
                  className="btn btn-primary"
                  type="button"
                  disabled={busyId === t.id}
                  onClick={() => void onCall(t, t.status === "called")}
                >
                  {t.status === "called" ? "재호출" : "호출"}
                </button>
                <button
                  className="btn btn-ghost"
                  type="button"
                  disabled={busyId === t.id}
                  onClick={() => void onStatus(t, "completed")}
                >
                  완료
                </button>
                <button
                  className="btn btn-ghost"
                  type="button"
                  disabled={busyId === t.id}
                  onClick={() => void onStatus(t, "no_show")}
                >
                  부재
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="queue muted-block">
        <h2>처리 완료</h2>
        <ul className="ticket-list compact">
          {done.map((t) => (
            <li key={t.id} className="ticket-row">
              <span className="num small">{t.number}</span>
              <span>
                {maskPhone(t.phone)} · {statusLabel(t.status)}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <Link className="text-link" to="/">
        홈
      </Link>
    </main>
  );
}

function maskPhone(phone: string) {
  if (phone.length < 8) return phone;
  return `${phone.slice(0, 3)}-****-${phone.slice(-4)}`;
}

function statusLabel(status: Ticket["status"]) {
  switch (status) {
    case "waiting":
      return "대기";
    case "called":
      return "호출됨";
    case "completed":
      return "완료";
    case "no_show":
      return "부재";
    case "cancelled":
      return "취소";
    default:
      return status;
  }
}
