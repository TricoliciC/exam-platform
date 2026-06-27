import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function AdminSettings() {
  const [settings, setSettings] = useState({
    site_name: '',
    logo_url: '',
    welcome_message: '',
    contact_email: ''
  })
  const [promoEmail, setPromoEmail] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/settings', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.settings) {
        setSettings(data.settings)
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(settings)
      })

      if (response.ok) {
        setMessage('Setările au fost actualizate cu succes!')
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      setMessage('Eroare la salvarea setărilor')
    }
  }

  const handlePromoteAdmin = async (e) => {
    e.preventDefault()
    setMessage('')

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/promote-admin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ email: promoEmail })
      })

      const data = await response.json()
      if (response.ok) {
        setMessage(data.message)
        setPromoEmail('')
      } else {
        setMessage(data.error || 'Eroare la promovare')
      }
    } catch (error) {
      console.error('Error promoting admin:', error)
      setMessage('Eroare la promovare')
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Setări Site</h1>
        <Link to="/admin" className="text-blue-600 hover:text-blue-800">
          ← Înapoi la Admin
        </Link>
      </div>

      {message && (
        <div className={`alert ${message.includes('Eroare') ? 'alert-error' : 'alert-success'} mb-6`}>
          {message}
        </div>
      )}

      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-4">Setări Generale</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="site_name">Nume Site</label>
            <input
              type="text"
              id="site_name"
              value={settings.site_name}
              onChange={(e) => setSettings({...settings, site_name: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label htmlFor="logo_url">URL Logo</label>
            <input
              type="text"
              id="logo_url"
              value={settings.logo_url}
              onChange={(e) => setSettings({...settings, logo_url: e.target.value})}
              placeholder="https://example.com/logo.png"
            />
          </div>
          <div className="form-group">
            <label htmlFor="welcome_message">Mesaj de Bun Venit</label>
            <textarea
              id="welcome_message"
              value={settings.welcome_message}
              onChange={(e) => setSettings({...settings, welcome_message: e.target.value})}
              rows="3"
            />
          </div>
          <div className="form-group">
            <label htmlFor="contact_email">Email de Contact</label>
            <input
              type="email"
              id="contact_email"
              value={settings.contact_email}
              onChange={(e) => setSettings({...settings, contact_email: e.target.value})}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Salvează Setări
          </button>
        </form>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">Promovează Utilizator la Admin</h2>
        <form onSubmit={handlePromoteAdmin}>
          <div className="form-group">
            <label htmlFor="promoEmail">Email Utilizator</label>
            <input
              type="email"
              id="promoEmail"
              value={promoEmail}
              onChange={(e) => setPromoEmail(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-success">
            Promovează la Admin
          </button>
        </form>
      </div>
    </div>
  )
}

export default AdminSettings
