import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'

function Home({ siteSettings }) {
  const [categories, setCategories] = useState([])

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/exams/categories')
      const data = await response.json()
      setCategories(data.categories)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          {siteSettings?.site_name || 'Platformă de Testare'}
        </h1>
        <p className="text-xl text-gray-600">
          {siteSettings?.welcome_message || 'Bine ai venit pe platforma noastră de testare!'}
        </p>
      </div>

      <h2 className="text-2xl font-bold mb-6">Categorii de Examene</h2>
      
      {categories.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <p>Nu există categorii de examene disponibile momentan.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category) => (
            <Link
              key={category.id}
              to={`/exams?category=${category.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <h3 className="text-xl font-bold mb-2">{category.name}</h3>
              <p className="text-gray-600">{category.description || 'Fără descriere'}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Home
