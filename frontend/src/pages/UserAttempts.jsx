import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function UserAttempts({ user }) {
  const [attempts, setAttempts] = useState([])

  useEffect(() => {
    if (user) {
      fetchAttempts()
    }
  }, [user])

  const fetchAttempts = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/exams/user/attempts', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setAttempts(data.attempts)
    } catch (error) {
      console.error('Error fetching attempts:', error)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Încercările Mele</h1>

      {attempts.length === 0 ? (
        <div className="card text-center py-8">
          <p className="text-gray-500">Nu ai încercat niciun examen încă.</p>
          <Link to="/exams" className="btn btn-primary mt-4 inline-block">
            Vezi Examene Disponibile
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {attempts.map((attempt) => (
            <div key={attempt.id} className="card">
              <h3 className="text-xl font-bold mb-2">{attempt.exam_title}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Data</p>
                  <p className="font-medium">
                    {new Date(attempt.started_at).toLocaleDateString('ro-RO')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Scor</p>
                  <p className={`font-bold ${attempt.score >= 50 ? 'text-green-600' : 'text-red-600'}`}>
                    {attempt.score.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Corecte</p>
                  <p className="font-medium">{attempt.correct_answers}/{attempt.total_questions}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className={`font-medium ${attempt.completed_at ? 'text-green-600' : 'text-yellow-600'}`}>
                    {attempt.completed_at ? 'Finalizat' : 'În curs'}
                  </p>
                </div>
              </div>
              {attempt.completed_at && (
                <Link
                  to={`/exams/${attempt.exam_id}/result/${attempt.id}`}
                  className="btn btn-primary"
                >
                  Vezi Detalii
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default UserAttempts
