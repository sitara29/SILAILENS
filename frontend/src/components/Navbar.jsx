import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

export default function Navbar() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user))
    supabase.auth.onAuthStateChange((_, session) => setUser(session?.user ?? null))
  }, [])

  const signOut = async () => {
    await supabase.auth.signOut()
    navigate('/')
  }

  return (
    <nav>
      <Link to="/" className="logo">SilaiLens</Link>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/collection">My Collection</Link>
            <button onClick={signOut} className="btn-nav" style={{border:'none',cursor:'pointer'}}>Sign Out</button>
          </>
        ) : (
          <>
            <Link to="/collection">My Collection</Link>
            <Link to="/signin" className="btn-nav">Sign In</Link>
          </>
        )}
      </div>
    </nav>
  )
}