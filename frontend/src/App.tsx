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
      <div className="home-bg" aria-hidden />
      <header className="home-brand">
        <p className="eyebrow">Wait Call</p>
        <h1>대기 호출</h1>
        <p className="lede">키오스크에서 등록하고, 호출 앱으로 카톡·문자 안내를 보냅니다.</p>
      </header>
      <nav className="home-actions">
        <Link className="btn btn-primary" to="/kiosk">
          키오스크
        </Link>
        <Link className="btn btn-secondary" to="/staff">
          호출 앱
        </Link>
      </nav>
    </main>
  );
}
