import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function AdminExams() {
  const [exams, setExams] = useState([])
  const [categories, setCategories] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingExam, setEditingExam] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category_id: '',
    pdf_file: null
  })

  useEffect(() => {
    fetchExams()
    fetchCategories()
  }, [])

  const fetchExams = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/exams/exams', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setExams(data.exams)
    } catch (error) {
      console.error('Error fetching exams:', error)
    }
  }

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
      const formDataToSend = new FormData()
      formDataToSend.append('title', formData.title)
      formDataToSend.append('description', formData.description)
      formDataToSend.append('category_id', formData.category_id)
      if (formData.pdf_file) {
        const isTxt = formData.pdf_file.name.toLowerCase().endsWith('.txt')
        formDataToSend.append(isTxt ? 'txt_file' : 'pdf_file', formData.pdf_file)
      }

      const response = await fetch('/api/admin/exams', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      })

      if (response.ok) {
        setShowForm(false)
        setFormData({ title: '', description: '', category_id: '', pdf_file: null })
        fetchExams()
        alert('Examen creat cu succes!')
      } else {
        const rawText = await response.text()
        console.error('Upload error response:', response.status, rawText)
        let msg = `Eroare ${response.status}`
        try {
          const data = JSON.parse(rawText)
          msg = data.error || msg
        } catch {
          msg = `${msg}: ${rawText.substring(0, 200)}`
        }
        alert(`EROARE: ${msg}`)
      }
    } catch (error) {
      console.error('Error saving exam:', error)
      alert(`Eroare retea: ${error.message}`)
    }
  }

  const handleEdit = async (exam) => {
    const newTitle = prompt('Noul titlu:', exam.title)
    const newDescription = prompt('Noua descriere:', exam.description)
    const newIsActive = confirm('Examenul este activ?')

    if (newTitle !== null) {
      try {
        const token = localStorage.getItem('token')
        const response = await fetch(`/api/admin/exams/${exam.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: newTitle,
            description: newDescription || exam.description,
            is_active: newIsActive
          })
        })

        if (response.ok) {
          fetchExams()
        }
      } catch (error) {
        console.error('Error updating exam:', error)
      }
    }
  }

  const handleDelete = async (examId) => {
    if (!window.confirm('Ești sigur că vrei să ștergi acest examen?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/admin/exams/${examId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        fetchExams()
      }
    } catch (error) {
      console.error('Error deleting exam:', error)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestionare Examene</h1>
        <Link to="/admin" className="text-blue-600 hover:text-blue-800">
          ← Înapoi la Admin
        </Link>
      </div>

      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="btn btn-primary mb-6"
        >
          + Încarcă Examen Nou
        </button>
      )}

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">Încarcă Examen Nou</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="title">Titlu Examen</label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
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
            <div className="form-group">
              <label htmlFor="category_id">Categorie</label>
              <select
                id="category_id"
                value={formData.category_id}
                onChange={(e) => setFormData({...formData, category_id: e.target.value})}
                required
              >
                <option value="">Selectează o categorie</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="pdf_file">Fișier întrebări (PDF sau TXT)</label>
              <input
                type="file"
                id="pdf_file"
                accept=".pdf,.txt"
                onChange={(e) => setFormData({...formData, pdf_file: e.target.files[0]})}
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                PDF sau TXT cu formatul: întrebări numerotate, opțiunile a) b) c) d), și linia "Correct: x"
              </p>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">
                Încarcă
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setFormData({ title: '', description: '', category_id: '', pdf_file: null })
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
        {exams.map((exam) => (
          <div key={exam.id} className={`card ${!exam.is_active ? 'opacity-60' : ''}`}>
            <h3 className="text-xl font-bold mb-2">{exam.title}</h3>
            <p className="text-gray-600 mb-2">{exam.description || 'Fără descriere'}</p>
            <p className="text-sm text-gray-500 mb-4">
              Categoria: {exam.category_name} | {exam.question_count} întrebări
            </p>
            {!exam.is_active && (
              <span className="inline-block bg-red-100 text-red-800 text-sm px-2 py-1 rounded mb-4">
                Inactiv
              </span>
            )}
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(exam)}
                className="btn btn-secondary"
              >
                Editează
              </button>
              <button
                onClick={() => handleDelete(exam.id)}
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

export default AdminExams
