import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState(null)
  const [error, setError] = useState(null)

  const signUp = async () => {
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) setError(error.message)
    else setMsg('Check your email for a confirmation link!')
  }

  return (
    <div className="page" style={{ maxWidth: '420px' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Create Account</h2>
      <p style={{ color: 'var(--text2)', marginBottom: '2rem' }}>Save your sculpture analyses to your personal collection.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
        <div><label>Email</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@email.com" /></div>
        <div><label>Password</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 6 characters" /></div>
      </div>

      {error && <p className="error-msg">{error}</p>}
      {msg && <p className="success-msg">{msg}</p>}

      <button className="btn-primary" style={{ width: '100%' }} onClick={signUp}>Create Account</button>
      <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text2)' }}>
        Already have one? <Link to="/signin" style={{ color: 'var(--ochre)', fontWeight: 600 }}>Sign In</Link>
      </p>
    </div>
  )
}