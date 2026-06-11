import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeImage } from '../lib/api'

export default function Analyze() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef()
  const navigate = useNavigate()

  const handleFile = (f) => {
    if (!f) return
    if (!['image/jpeg','image/png','image/webp'].includes(f.type)) {
      setError('Please upload a JPEG, PNG, or WEBP image.'); return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File too large. Max 10MB.'); return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setError(null)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    handleFile(e.dataTransfer.files[0])
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true); setError(null)
    try {
      const result = await analyzeImage(file)
      // ✅ Save under 'lastA' so Results.jsx can read it
      sessionStorage.setItem('lastA', JSON.stringify(result))
      navigate('/results')
    } catch (e) {
      setError('Analysis failed. Is the backend running on localhost:8000?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h2 style={{ marginBottom: '0.5rem' }}>Upload a Sculpture</h2>
      <p style={{ color: 'var(--text2)', marginBottom: '2rem' }}>
        Take a photo or upload from your gallery. Accepted: JPEG, PNG, WEBP · Max 10MB
      </p>

      {/* Drop zone */}
      <div
        onClick={() => inputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        style={{
          border: `2px dashed ${preview ? 'var(--ochre)' : '#D4C4BA'}`,
          borderRadius: '12px', padding: '2rem',
          textAlign: 'center', cursor: 'pointer',
          background: preview ? 'transparent' : 'white',
          transition: 'border-color .2s',
          marginBottom: '1.5rem',
          minHeight: '240px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        {preview ? (
          <img src={preview} alt="preview" style={{ maxHeight: '300px', maxWidth: '100%', borderRadius: '8px' }} />
        ) : (
          <div>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🏛️</div>
            <p style={{ fontWeight: 500 }}>Click to upload or drag & drop</p>
            <p style={{ color: 'var(--text2)', fontSize: '0.875rem', marginTop: '4px' }}>Sculpture photo goes here</p>
          </div>
        )}
      </div>

      <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: 'none' }}
        onChange={e => handleFile(e.target.files[0])} />

      {/* Camera button for mobile */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button className="btn-secondary" style={{ flex: 1 }} onClick={() => inputRef.current.click()}>
          📁 Upload from Gallery
        </button>
        <label style={{ flex: 1 }}>
          <input type="file" accept="image/*" capture="environment" style={{ display: 'none' }}
            onChange={e => handleFile(e.target.files[0])} />
          <span className="btn-secondary" style={{ display: 'block', textAlign: 'center', cursor: 'pointer' }}>
            📷 Take Photo
          </span>
        </label>
      </div>

      {error && <p className="error-msg">{error}</p>}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner" />
          <p style={{ marginTop: '1rem', color: 'var(--text2)' }}>Analyzing sculpture...</p>
        </div>
      ) : (
        <button className="btn-primary" style={{ width: '100%', opacity: file ? 1 : 0.5 }}
          onClick={handleAnalyze} disabled={!file}>
          Analyze Sculpture
        </button>
      )}
    </div>
  )
}
