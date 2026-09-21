import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [factoryState, setFactoryState] = useState(null);
  const [error, setError] = useState(null);

  const fetchState = async () => {
    try {
      const response = await fetch('http://localhost:8000/state');
      if (!response.ok) {
        throw new Error('API bağlantısı başarısız');
      }
      const data = await response.json();
      setFactoryState(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 2000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="container">
        <h2>⚠️ Bağlantı Hatası</h2>
        <p>FastAPI sunucusuna ulaşılamadı. `uvicorn api:app --reload` çalışıyor mu?</p>
        <p className="error-text">{error}</p>
      </div>
    );
  }

  if (!factoryState) {
    return (
      <div className="container">
        <h2>Fabrika İkizi Yükleniyor...</h2>
        <p>Simülasyon verisi bekleniyor.</p>
      </div>
    );
  }

  const { elapsed_time, bottleneck, wip, machines } = factoryState;

  return (
    <div className="dashboard">
      <header className="header">
        <h1>🏭 Digital Factory Twin</h1>
        <div className="header-meta">
          <span>⏱️ Çalışma Süresi: <strong>{elapsed_time}s</strong></span>
          <span className="live-badge">● CANLI</span>
        </div>
      </header>

      {bottleneck && bottleneck.machine && (
        <section className="bottleneck-banner">
          <div className="bottleneck-title">🚨 TESPİT EDİLEN DARBOĞAZ (BOTTLENECK)</div>
          <div className="bottleneck-detail">
            <strong>{bottleneck.machine}</strong> istasyonu <strong>%{bottleneck.utilization}</strong> dolulukla hattı sınırlıyor.
          </div>
        </section>
      )}

      <section className="section">
        <h2>📦 Ara Stok Bantları (WIP)</h2>
        <div className="wip-grid">
          {Object.entries(wip).map(([bandName, count]) => (
            <div key={bandName} className="wip-card">
              <span className="wip-name">{bandName}</span>
              <span className="wip-count">{count} <small>adet</small></span>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>⚙️ İstasyonlar ve Kullanım Oranları</h2>
        <div className="machines-grid">
          {machines.map((m) => {
            const isBottleneck = bottleneck?.machine === m.name;
            const statusClass = m.status.toLowerCase();

            return (
              <div key={m.id} className={`machine-card ${isBottleneck ? 'is-bottleneck' : ''}`}>
                <div className="machine-header">
                  <h3>{m.name}</h3>
                  <span className={`status-pill ${statusClass}`}>{m.status}</span>
                </div>

                <div className="metric-row">
                  <span>Kullanım (Utilization):</span>
                  <strong>%{m.utilization}</strong>
                </div>
                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${Math.min(m.utilization, 100)}%` }}
                  />
                </div>

                <div className="production-stats">
                  <div>
                    <span className="stat-label">Sağlam</span>
                    <span className="stat-val good">{m.good_produced}</span>
                  </div>
                  <div>
                    <span className="stat-label">Hurda</span>
                    <span className="stat-val scrap">{m.scrap_produced}</span>
                  </div>
                  <div>
                    <span className="stat-label">Toplam</span>
                    <span className="stat-val total">{m.total_produced}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

export default App;