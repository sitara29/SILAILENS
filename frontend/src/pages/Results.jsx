import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

const ORNAMENT_LABELS = {
  headwear: { label: 'Headwear', icon: '👑' },
  weapons: { label: 'Weapons', icon: '⚔️' },
  waistbands: { label: 'Waistbands', icon: '🔶' },
  leg_ornaments: { label: 'Leg Ornaments', icon: '💎' },
}

export default function Results() {
  const [result, setResult] = useState(null)
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const raw = sessionStorage.getItem('lastA') // ✅ matches Analyze.jsx
    if (!raw) { navigate('/analyze'); return }
    setResult(JSON.parse(raw))
    setLoading(false)
  }, [])

  const handleSave = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) { navigate('/signin'); return }
    setSaving(true)
    await supabase.from('analyses').update({ user_id: user.id }).eq('id', result.analysis_id)
    setSaving(false)
    setSaved(true)
  }

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(result.metadata, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `silaielns_${result.analysis_id}.json`
    a.click()
  }

  if (loading) {
    return (
      <div className="page">
        <p style={{ textAlign: 'center', fontSize: '1.2rem', marginTop: '2rem' }}>
          🔍 Loading analysis results...
        </p>
      </div>
    )
  }

  if (!result) return null

  const pct = Math.round(result.dynasty_confidence * 100)

  return (
    <div className="page">
      {/* Image */}
      {result.image_url && (
        <img src={result.image_url} alt="sculpture"
          style={{ width: '100%', maxHeight: '300px', objectFit: 'cover', borderRadius: '12px', marginBottom: '1.5rem' }} />
      )}

      {/* Dynasty */}
      <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--ochre)' }}>
        <p style={{ color: 'var(--text2)', fontSize: '0.85rem', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Identified Dynasty
        </p>
        <h2 style={{ color: 'var(--dynasty)', fontSize: '2rem', marginBottom: '8px' }}>
          {result.dynasty} Dynasty
        </h2>
        <p style={{ fontWeight: 600, color: 'var(--ochre)', marginBottom: '8px' }}>
          {pct}% confidence
        </p>
        <div className="conf-bar-wrap">
          <div className="conf-bar-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* Ornaments */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Ornament Detection</h3>
        {Object.entries(result.ornaments).map(([key, val]) => {
          const meta = ORNAMENT_LABELS[key]
          return (
            <div key={key} className="ornament-row">
              <span className="ornament-icon">{meta.icon}</span>
              <span className="ornament-name">{meta.label}</span>
              <span className={`ornament-conf ${val.present ? 'detected' : 'undetected'}`}>
                {val.present ? '✓ Detected' : '✗ Not detected'}
              </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text2)', minWidth: '48px', textAlign: 'right' }}>
                {Math.round(val.confidence * 100)}%
              </span>
            </div>
          )
        })}
      </div>

      {/* Historical Context */}
      <div className="card" style={{ marginBottom: '1.5rem', background: '#FDF6F0' }}>
        <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Historical Context</h3>
        <p style={{ lineHeight: 1.8, color: 'var(--brown)', fontSize: '0.95rem' }}>
          {result.historical_context}
        </p>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {saved ? (
          <p className="success-msg" style={{ textAlign: 'center', fontSize: '1rem' }}>
            ✓ Saved to your collection!
          </p>
        ) : (
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save to My Collection'}
          </button>
        )}
        <button className="btn-secondary" onClick={handleDownload}>
          ⬇ Download JSON Metadata
        </button>
        <button className="btn-secondary" onClick={() => { sessionStorage.removeItem('lastA'); navigate('/analyze') }}>
          Analyze Another
        </button>
      </div>
    </div>
  )
}
