import { Link, Navigate, Route, Routes } from "react-router-dom";
import KioskPage from "./pages/KioskPage";
import StaffPage from "./pages/StaffPage";

export default function App() {
  return (
    <div className="app-shell">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/kiosk" element={<KioskPage />} />
        <Route path="/staff" element={<StaffPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

function Home() {
  return (
    <main className="home">
      <div className="atmosphere" aria-hidden>
        <div className="atmosphere-wash" />
        <div className="atmosphere-grid" />
        <div className="atmosphere-orb atmosphere-orb-a" />
        <div className="atmosphere-orb atmosphere-orb-b" />
      </div>

      <div className="home-stage reveal">
        <p className="brand-mark">WAIT CALL</p>
        <h1 className="brand-title">
          대기
          <span className="brand-slash">/</span>
          호출
        </h1>
        <p className="home-line">등록은 키오스크에서, 안내는 호출 한 번으로.</p>
        <nav className="home-actions" aria-label="모드 선택">
          <Link className="btn btn-ink" to="/kiosk">
            키오스크
          </Link>
          <Link className="btn btn-lagoon" to="/staff">
            호출 앱
          </Link>
        </nav>
      </div>
    </main>
  );
}
