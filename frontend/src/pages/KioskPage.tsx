import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { registerTicket, TicketCallOut } from "../api/client";

const STORE_SLUG = import.meta.env.VITE_STORE_SLUG || "demo";

export default function KioskPage() {
  const [phone, setPhone] = useState("");
  const [partySize, setPartySize] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TicketCallOut | null>(null);

  const displayPhone = useMemo(() => formatPhone(phone), [phone]);
  const hasInput = phone.length > 0;

  function press(digit: string) {
    if (phone.length >= 11) return;
    setPhone((p) => p + digit);
  }

  function press010() {
    setPhone((p) => {
      if (p.startsWith("010")) return p;
      if (!p) return "010";
      return ("010" + p).slice(0, 11);
    });
  }

  function backspace() {
    setPhone((p) => p.slice(0, -1));
  }

  function clear() {
    setPhone("");
    setError(null);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const out = await registerTicket(phone, partySize, STORE_SLUG);
      setResult(out);
      setPhone("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "등록에 실패했습니다");
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    return (
      <main className="kiosk success-view">
        <div className="atmosphere" aria-hidden>
          <div className="atmosphere-wash" />
          <div className="atmosphere-orb atmosphere-orb-a" />
        </div>
        <div className="success-panel reveal">
          <p className="brand-mark">WAIT CALL</p>
          <p className="soft-label">등록 완료</p>
          <p className="ticket-number" aria-live="polite">
            {result.ticket.number}
          </p>
          <p className="success-line">대기번호가 발급되었습니다</p>
          <p className="meta">
            {maskPhone(result.ticket.phone)}
            <span className="dot">·</span>
            {channelLabel(result.channel)} 안내
          </p>
          <button className="btn btn-ink wide" type="button" onClick={() => setResult(null)}>
            다음 고객
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="kiosk">
      <div className="atmosphere" aria-hidden>
        <div className="atmosphere-wash" />
        <div className="atmosphere-grid" />
        <div className="atmosphere-orb atmosphere-orb-b" />
      </div>

      <div className="kiosk-stage reveal">
        <header className="kiosk-header">
          <div className="kiosk-brand-row">
            <p className="brand-mark">WAIT CALL</p>
            <Link className="quiet-link" to="/">
              홈
            </Link>
          </div>
          <h1 className="page-title">전화번호</h1>
          <p className="page-sub">입력하시면 대기번호를 보내드립니다.</p>
        </header>

        <form className="kiosk-panel" onSubmit={onSubmit}>
          <div
            className={`phone-display ${hasInput ? "is-filled" : ""}`}
            aria-live="polite"
          >
            {displayPhone || "010 — — — —"}
          </div>

          <div className="party-row">
            <span className="soft-label">인원</span>
            <div className="party-steps" role="group" aria-label="인원 선택">
              {Array.from({ length: 6 }, (_, i) => i + 1).map((n) => (
                <button
                  key={n}
                  type="button"
                  className={`party-chip ${partySize === n ? "is-active" : ""}`}
                  onClick={() => setPartySize(n)}
                >
                  {n}
                </button>
              ))}
              <select
                className="party-more"
                aria-label="인원 더보기"
                value={partySize > 6 ? partySize : ""}
                onChange={(e) => setPartySize(Number(e.target.value))}
              >
                <option value="" disabled>
                  +
                </option>
                {[7, 8, 9, 10].map((n) => (
                  <option key={n} value={n}>
                    {n}명
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="button"
            className="key key-prefix"
            onClick={press010}
            aria-label="010 입력"
          >
            010
          </button>

          <div className="keypad">
            {"123456789".split("").map((d) => (
              <button key={d} type="button" className="key" onClick={() => press(d)}>
                {d}
              </button>
            ))}
            <button type="button" className="key key-muted" onClick={clear}>
              C
            </button>
            <button type="button" className="key" onClick={() => press("0")}>
              0
            </button>
            <button type="button" className="key key-muted" onClick={backspace}>
              ⌫
            </button>
          </div>

          {error && <p className="error">{error}</p>}

          <button
            className="btn btn-ink wide"
            type="submit"
            disabled={loading || phone.length < 10}
          >
            {loading ? "보내는 중…" : "대기번호 받기"}
          </button>
        </form>
      </div>
    </main>
  );
}

function formatPhone(digits: string) {
  if (digits.length <= 3) return digits;
  if (digits.length <= 7) return `${digits.slice(0, 3)} ${digits.slice(3)}`;
  return `${digits.slice(0, 3)} ${digits.slice(3, 7)} ${digits.slice(7, 11)}`;
}

function maskPhone(phone: string) {
  if (phone.length < 8) return phone;
  return `${phone.slice(0, 3)} **** ${phone.slice(-4)}`;
}

function channelLabel(channel: string) {
  if (channel === "kakao") return "카카오톡";
  if (channel === "sms") return "문자";
  if (channel === "console") return "테스트";
  return channel;
}
