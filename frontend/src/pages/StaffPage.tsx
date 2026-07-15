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
      setToast(`${ticket.number}번 · ${channelLabel(out.channel)} 전송`);
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
      <div className="atmosphere atmosphere-soft" aria-hidden>
        <div className="atmosphere-wash" />
        <div className="atmosphere-grid" />
      </div>

      <div className="staff-stage reveal">
        <header className="staff-header">
          <div>
            <div className="kiosk-brand-row">
              <p className="brand-mark">WAIT CALL</p>
              <Link className="quiet-link" to="/">
                홈
              </Link>
            </div>
            <h1 className="page-title">대기열</h1>
            <p className="page-sub">오늘 · {STORE_SLUG}</p>
          </div>
          <button className="btn btn-ghost" type="button" onClick={() => void refresh()}>
            새로고침
          </button>
        </header>

        {toast && (
          <div className="toast" role="status">
            <span>{toast}</span>
            <button type="button" onClick={() => setToast(null)}>
              닫기
            </button>
          </div>
        )}

        {error && <p className="error">{error}</p>}
        {loading && <p className="meta">불러오는 중…</p>}

        <section className="queue" aria-label="대기 및 호출중">
          <div className="section-head">
            <h2>진행</h2>
            <span className="count">{active.length}</span>
          </div>
          {active.length === 0 && !loading && (
            <p className="empty-line">대기 중인 고객이 없습니다.</p>
          )}
          <ul className="ticket-list">
            {active.map((t, index) => (
              <li
                key={t.id}
                className={`ticket-row status-${t.status}`}
                style={{ animationDelay: `${index * 40}ms` }}
              >
                <div className="ticket-main">
                  <span className="num">{t.number}</span>
                  <div className="ticket-copy">
                    <strong>{maskPhone(t.phone)}</strong>
                    <p className="meta">
                      {t.party_size}명
                      <span className="dot">·</span>
                      {statusLabel(t.status)}
                    </p>
                  </div>
                </div>
                <div className="ticket-actions">
                  <button
                    className="btn btn-lagoon"
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

        <section className="queue queue-done" aria-label="처리 완료">
          <div className="section-head">
            <h2>완료</h2>
            <span className="count">{done.length}</span>
          </div>
          <ul className="ticket-list compact">
            {done.map((t) => (
              <li key={t.id} className="ticket-row done-row">
                <span className="num small">{t.number}</span>
                <span className="done-copy">
                  {maskPhone(t.phone)}
                  <span className="dot">·</span>
                  {statusLabel(t.status)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>
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

function channelLabel(channel: string) {
  if (channel === "kakao") return "카카오톡";
  if (channel === "sms") return "문자";
  if (channel === "console") return "테스트";
  return channel;
}
