import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const signInEmail = async () => {
    setLoading(true); setError(null)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) { setError(error.message); setLoading(false) }
    else navigate('/collection')
  }

  const signInGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/collection' }
    })
  }

  return (
    <div className="page" style={{ maxWidth: '420px' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Sign In</h2>
      <p style={{ color: 'var(--text2)', marginBottom: '2rem' }}>Sign in to save and view your sculpture analyses.</p>

      <button className="btn-primary" style={{ width: '100%', marginBottom: '1.5rem', background: 'white', color: 'var(--brown)', border: '1.5px solid #E5DDD8' }} onClick={signInGoogle}>
        Sign in with Google
      </button>

      <div style={{ textAlign: 'center', color: 'var(--text2)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>or</div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
        <div><label>Email</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@email.com" /></div>
        <div><label>Password</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" /></div>
      </div>

      {error && <p className="error-msg">{error}</p>}

      <button className="btn-primary" style={{ width: '100%', marginTop: '1rem' }} onClick={signInEmail} disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>

      <p style={{ textAlign: 'center', marginTop: '0.75rem', fontSize: '0.85rem' }}>
  <span style={{ color: 'var(--ochre)', cursor: 'pointer' }} 
    onClick={async () => {
      if (!email) { setError('Enter your email first'); return }
      await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: window.location.origin + '/signin'
      })
      setError(null)
      alert('Password reset email sent! Check your inbox.')
    }}>
    Forgot password?
  </span>
</p>

      <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text2)' }}>
        No account? <Link to="/signup" style={{ color: 'var(--ochre)', fontWeight: 600 }}>Sign Up</Link>
      </p>
    </div>
  )
}