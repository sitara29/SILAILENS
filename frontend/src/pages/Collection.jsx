import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function Collection() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) { navigate('/signin'); return }
      const { data } = await supabase.from('analyses').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
      setAnalyses(data || [])
      setLoading(false)
    }
    load()
  }, [])

  if (loading) return <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}><div className="spinner" /></div>

  return (
    <div className="page-wide">
      <h2 style={{ marginBottom: '0.5rem' }}>My Collection</h2>
      <p style={{ color: 'var(--text2)', marginBottom: '2rem' }}>Your saved sculpture analyses</p>

      {analyses.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text2)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏛️</div>
          <p>No analyses saved yet.</p>
          <button className="btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/analyze')}>Upload your first sculpture</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
          {analyses.map(a => (
            <div key={a.id} className="card" style={{ cursor: 'pointer' }}>
              {a.image_url && <img src={a.image_url} alt="sculpture" style={{ width: '100%', height: '160px', objectFit: 'cover', borderRadius: '8px', marginBottom: '1rem' }} />}
              <p style={{ fontWeight: 600, color: 'var(--dynasty)', marginBottom: '4px' }}>{a.dynasty} Dynasty</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text2)', marginBottom: '0.75rem' }}>
                {new Date(a.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
              </p>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {['headwear','weapons','waistbands','leg_ornaments'].filter(k => a[`${k}_present`]).map(k => (
                  <span key={k} style={{ background: '#FDF6F0', color: 'var(--ochre)', fontSize: '0.75rem', padding: '3px 10px', borderRadius: '20px', fontWeight: 500 }}>
                    {k.replace('_',' ')}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}