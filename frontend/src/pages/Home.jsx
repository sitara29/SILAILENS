import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <p style={{ color: 'var(--ochre)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '1rem' }}>
        AI Heritage Analysis
      </p>
      <h1 style={{ fontSize: '3rem', lineHeight: 1.2, marginBottom: '1rem' }}>
        Uncover the dynasty<br />in every sculpture
      </h1>
      <p style={{ color: 'var(--text2)', fontSize: '1.1rem', maxWidth: '480px', margin: '0 auto 2.5rem', lineHeight: 1.7 }}>
        Upload a photo of a temple sculpture. SilaiLens detects ornamental features and identifies its dynasty using machine learning.
      </p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link to="/analyze" className="btn-primary">Upload a Sculpture</Link>
        <Link to="/collection" className="btn-secondary">My Collection</Link>
      </div>
      <div style={{ marginTop: '4rem', display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        {['Chola Dynasty', 'Pallava (coming)', 'JSON Archival Export'].map(f => (
          <div key={f} style={{ background: 'white', borderRadius: '8px', padding: '12px 20px', fontSize: '0.9rem', color: 'var(--dynasty)', fontWeight: 500, boxShadow: '0 1px 6px rgba(59,26,8,.08)' }}>
            {f}
          </div>
        ))}
      </div>
    </div>
  )
}