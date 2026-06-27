import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'

function ExamList({ user }) {
  const [searchParams] = useSearchParams()
  const categoryId = searchParams.get('category')
  const [exams, setExams] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(categoryId || '')

  useEffect(() => {
    fetchCategories()
    fetchExams()
  }, [selectedCategory])

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/exams/categories')
      const data = await response.json()
      setCategories(data.categories)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const fetchExams = async () => {
    try {
      let url = '/api/exams/exams'
      if (selectedCategory) {
        url += `?category_id=${selectedCategory}`
      }
      const response = await fetch(url)
      const data = await response.json()
      setExams(data.exams)
    } catch (error) {
      console.error('Error fetching exams:', error)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Examene Disponibile</h1>
      
      <div className="mb-6">
        <label className="block mb-2 font-medium">Filtrează după categorie:</label>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="w-full max-w-md p-2 border rounded"
        >
          <option value="">Toate categoriile</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {exams.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <p>Nu există examene disponibile în această categorie.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => (
            <div key={exam.id} className="card">
              <h3 className="text-xl font-bold mb-2">{exam.title}</h3>
              <p className="text-gray-600 mb-4">{exam.description || 'Fără descriere'}</p>
              <p className="text-sm text-gray-500 mb-4">
                Categoria: {exam.category_name} | {exam.question_count} întrebări
              </p>
              <Link
                to={`/exams/${exam.id}`}
                className="btn btn-primary w-full text-center"
              >
                Vezi Detalii
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ExamList
