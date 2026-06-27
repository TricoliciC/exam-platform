import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'

function ExamDetail({ user }) {
  const { id } = useParams()
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchExam()
  }, [id])

  const fetchExam = async () => {
    try {
      const response = await fetch(`/api/exams/exams/${id}`)
      const data = await response.json()
      setExam(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching exam:', error)
      setLoading(false)
    }
  }

  const startExam = async () => {
    if (!user) {
      alert('Trebuie să fii logat pentru a începe testul')
      navigate('/login')
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/exams/attempts/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ exam_id: id })
      })

      const data = await response.json()
      if (response.ok) {
        navigate(`/exams/${id}/test`, { state: { attemptId: data.attempt_id, questions: data.questions } })
      } else {
        alert(data.error || 'Eroare la pornirea testului. Verifica daca esti logat.')
      }
    } catch (error) {
      console.error('Error starting exam:', error)
      alert('Eroare de retea. Verifica conexiunea la server.')
    }
  }

  if (loading) {
    return <div className="text-center py-8">Încărcare...</div>
  }

  if (!exam) {
    return <div className="text-center py-8">Examenul nu a fost găsit</div>
  }

  return (
    <div>
      <Link to="/exams" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
        ← Înapoi la examene
      </Link>
      
      <div className="card">
        <h1 className="text-3xl font-bold mb-4">{exam.exam.title}</h1>
        <p className="text-gray-600 mb-4">{exam.exam.description || 'Fără descriere'}</p>
        
        <div className="bg-gray-50 p-4 rounded mb-6">
          <p><strong>Categorie:</strong> {exam.exam.category_name}</p>
          <p><strong>Număr întrebări:</strong> {exam.questions.length}</p>
        </div>

        <button
          onClick={startExam}
          className="btn btn-primary w-full text-lg py-3"
        >
          Începe Testul
        </button>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">Previzualizare Întrebări</h2>
        {exam.questions.slice(0, 3).map((q, index) => (
          <div key={q.id} className="mb-4 pb-4 border-b">
            <p className="font-medium">{index + 1}. {q.question_text}</p>
            <div className="ml-4 mt-2 text-gray-600">
              <p>a) {q.option_a}</p>
              <p>b) {q.option_b}</p>
              <p>c) {q.option_c}</p>
              <p>d) {q.option_d}</p>
            </div>
          </div>
        ))}
        {exam.questions.length > 3 && (
          <p className="text-gray-500">... și încă {exam.questions.length - 3} întrebări</p>
        )}
      </div>
    </div>
  )
}

export default ExamDetail
