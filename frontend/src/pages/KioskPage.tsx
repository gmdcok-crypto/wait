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

  function press(digit: string) {
    if (phone.length >= 11) return;
    setPhone((p) => p + digit);
  }

  function backspace() {
    setPhone((p) => p.slice(0, -1));
  }

  function clear() {
    setPhone("");
    setError(null);
    setResult(null);
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
        <p className="eyebrow">등록 완료</p>
        <h1 className="ticket-number">{result.ticket.number}</h1>
        <p className="lede">대기번호가 발급되었습니다</p>
        <p className="meta">
          {maskPhone(result.ticket.phone)} · {result.channel} 안내
        </p>
        <p className="message">{result.message}</p>
        <button className="btn btn-primary" type="button" onClick={() => setResult(null)}>
          다음 고객
        </button>
        <Link className="text-link" to="/">
          홈
        </Link>
      </main>
    );
  }

  return (
    <main className="kiosk">
      <header className="kiosk-header">
        <p className="eyebrow">키오스크 · {STORE_SLUG}</p>
        <h1>전화번호 입력</h1>
        <p className="lede">대기번호를 카카오톡 또는 문자로 보내드립니다.</p>
      </header>

      <form className="kiosk-form" onSubmit={onSubmit}>
        <div className="phone-display" aria-live="polite">
          {displayPhone || "010-0000-0000"}
        </div>

        <label className="party">
          인원
          <select
            value={partySize}
            onChange={(e) => setPartySize(Number(e.target.value))}
          >
            {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
              <option key={n} value={n}>
                {n}명
              </option>
            ))}
          </select>
        </label>

        <div className="keypad">
          {"123456789".split("").map((d) => (
            <button key={d} type="button" className="key" onClick={() => press(d)}>
              {d}
            </button>
          ))}
          <button type="button" className="key muted" onClick={clear}>
            C
          </button>
          <button type="button" className="key" onClick={() => press("0")}>
            0
          </button>
          <button type="button" className="key muted" onClick={backspace}>
            ←
          </button>
        </div>

        {error && <p className="error">{error}</p>}

        <button className="btn btn-primary wide" type="submit" disabled={loading || phone.length < 10}>
          {loading ? "전송 중…" : "대기번호 받기"}
        </button>
      </form>

      <Link className="text-link" to="/">
        홈
      </Link>
    </main>
  );
}

function formatPhone(digits: string) {
  if (digits.length <= 3) return digits;
  if (digits.length <= 7) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
  return `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7, 11)}`;
}

function maskPhone(phone: string) {
  if (phone.length < 8) return phone;
  return `${phone.slice(0, 3)}-****-${phone.slice(-4)}`;
}
