import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function AdminCategories() {
  const [categories, setCategories] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  })

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/exams/categories', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setCategories(data.categories)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const token = localStorage.getItem('token')
      const url = editingCategory 
        ? `/api/admin/categories/${editingCategory.id}`
        : '/api/admin/categories'
      
      const method = editingCategory ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setShowForm(false)
        setEditingCategory(null)
        setFormData({ name: '', description: '' })
        fetchCategories()
      }
    } catch (error) {
      console.error('Error saving category:', error)
    }
  }

  const handleEdit = (category) => {
    setEditingCategory(category)
    setFormData({
      name: category.name,
      description: category.description
    })
    setShowForm(true)
  }

  const handleDelete = async (categoryId) => {
    if (!window.confirm('Ești sigur că vrei să ștergi această categorie?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/categories/${categoryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        fetchCategories()
      }
    } catch (error) {
      console.error('Error deleting category:', error)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestionare Categorii</h1>
        <Link to="/admin" className="text-blue-600 hover:text-blue-800">
          ← Înapoi la Admin
        </Link>
      </div>

      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="btn btn-primary mb-6"
        >
          + Adaugă Categorie Nouă
        </button>
      )}

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">
            {editingCategory ? 'Editează Categorie' : 'Adaugă Categorie Nouă'}
          </h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Nume Categorie</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Descriere</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows="3"
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">
                {editingCategory ? 'Actualizează' : 'Adaugă'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditingCategory(null)
                  setFormData({ name: '', description: '' })
                }}
                className="btn btn-secondary"
              >
                Anulează
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((category) => (
          <div key={category.id} className="card">
            <h3 className="text-xl font-bold mb-2">{category.name}</h3>
            <p className="text-gray-600 mb-4">{category.description || 'Fără descriere'}</p>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(category)}
                className="btn btn-secondary"
              >
                Editează
              </button>
              <button
                onClick={() => handleDelete(category.id)}
                className="btn btn-danger"
              >
                Șterge
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AdminCategories
