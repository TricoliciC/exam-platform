import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function AdminUsers() {
  const [users, setUsers] = useState([])
  const [editingUser, setEditingUser] = useState(null)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    is_admin: false,
    password: ''
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      setUsers(data.users || [])
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const openEdit = (user) => {
    setEditingUser(user)
    setFormData({
      username: user.username,
      email: user.email,
      is_admin: user.is_admin,
      password: ''
    })
    setMessage({ type: '', text: '' })
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      const token = localStorage.getItem('token')
      const payload = { ...formData }
      if (!payload.password) delete payload.password

      const response = await fetch(`/api/admin/users/${editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()
      if (response.ok) {
        setMessage({ type: 'success', text: 'Utilizator actualizat cu succes!' })
        setEditingUser(null)
        fetchUsers()
      } else {
        setMessage({ type: 'error', text: data.error || 'Eroare la salvare' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Eroare retea: ' + error.message })
    }
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('Esti sigur ca vrei sa stergi acest utilizator?')) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Utilizator sters!' })
        fetchUsers()
      } else {
        const data = await response.json()
        setMessage({ type: 'error', text: data.error || 'Eroare la stergere' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Eroare retea: ' + error.message })
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestionare Utilizatori</h1>
        <Link to="/admin" className="text-blue-600 hover:text-blue-800">
          ← Înapoi la Admin
        </Link>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg mb-4 ${
          message.type === 'success' ? 'bg-green-100 text-green-700 border border-green-300'
            : 'bg-red-100 text-red-700 border border-red-300'
        }`}>
          {message.text}
        </div>
      )}

      {/* Editare utilizator */}
      {editingUser && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 shadow-xl">
            <h2 className="text-xl font-bold mb-4">
              Editeaza: {editingUser.username}
            </h2>
            <form onSubmit={handleSave}>
              <div className="form-group">
                <label>Nume utilizator</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_admin}
                    onChange={(e) => setFormData({...formData, is_admin: e.target.checked})}
                    className="w-5 h-5"
                  />
                  <span>Administrator</span>
                </label>
              </div>
              <div className="form-group">
                <label>Parola noua (lasa gol daca nu vrei sa schimbi)</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="Lasa gol pentru a pastra parola veche"
                />
              </div>
              <div className="flex gap-2 mt-4">
                <button type="submit" className="btn btn-primary flex-1">
                  Salveaza
                </button>
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="btn btn-secondary"
                >
                  Anuleaza
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista utilizatori */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="py-3 px-4 font-semibold text-gray-700">ID</th>
                <th className="py-3 px-4 font-semibold text-gray-700">Utilizator</th>
                <th className="py-3 px-4 font-semibold text-gray-700">Email</th>
                <th className="py-3 px-4 font-semibold text-gray-700">Admin</th>
                <th className="py-3 px-4 font-semibold text-gray-700">Creat la</th>
                <th className="py-3 px-4 font-semibold text-gray-700">Actiuni</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-gray-500">
                    Nu exista utilizatori
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">{u.id}</td>
                    <td className="py-3 px-4 font-medium">{u.username}</td>
                    <td className="py-3 px-4 text-gray-600">{u.email}</td>
                    <td className="py-3 px-4">
                      {u.is_admin ? (
                        <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm font-medium">
                          Da
                        </span>
                      ) : (
                        <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm">
                          Nu
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-sm">
                      {u.created_at ? new Date(u.created_at).toLocaleDateString('ro-RO') : '-'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEdit(u)}
                          className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                        >
                          Editeaza
                        </button>
                        <button
                          onClick={() => handleDelete(u.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          Sterge
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card mt-4 text-sm text-gray-500">
        <p><strong>Nota:</strong> parolele nu pot fi vizualizate din motive de securitate. Poti doar sa resetezi parola unui utilizator (seteaza una noua).</p>
      </div>
    </div>
  )
}

export default AdminUsers
