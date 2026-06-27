import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

function ExamResult({ user }) {
  const { id, attemptId } = useParams()
  const [attempt, setAttempt] = useState(null)
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchResult()
  }, [attemptId])

  const fetchResult = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/exams/attempts/${attemptId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setAttempt(data.attempt)
      setAnswers(data.answers)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching result:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Încărcare...</div>
  }

  if (!attempt) {
    return <div className="text-center py-8">Rezultatul nu a fost găsit</div>
  }

  const percentage = attempt.score || 0
  const passed = percentage >= 50
  const total = attempt.total_questions || 0
  const correct = attempt.correct_answers || 0
  const wrong = Math.max(0, total - correct)
  const unanswered = Math.max(0, (attempt.questions_total || 0) - total)

  return (
    <div>
      <Link to="/exams" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
        ← Inapoi la examene
      </Link>

      <div className={`card ${passed ? 'border-green-500' : 'border-red-500'}`}>
        <h1 className="text-3xl font-bold mb-4">Rezultat Test</h1>

        <div className="text-center py-8">
          <div className={`text-6xl font-bold mb-4 ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {percentage.toFixed(1)}%
          </div>
          <p className={`text-2xl ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {passed ? 'AI TRECUT!' : 'NU AI TRECUT'}
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 text-center">
          <div className="bg-blue-50 p-4 rounded">
            <div className="text-2xl font-bold text-blue-600">{total}</div>
            <div className="text-gray-600">Raspunsuri date</div>
          </div>
          <div className="bg-green-50 p-4 rounded">
            <div className="text-2xl font-bold text-green-600">{correct}</div>
            <div className="text-gray-600">Corecte</div>
          </div>
          <div className="bg-red-50 p-4 rounded">
            <div className="text-2xl font-bold text-red-600">{wrong}</div>
            <div className="text-gray-600">Gresite</div>
          </div>
        </div>
      </div>

      {/* DEBUG: raw data */}
      {process.env.NODE_ENV === 'development' && (
        <details className="card mb-4" style={{ background: '#f0f0f0' }}>
          <summary className="font-bold cursor-pointer">Debug: date brute</summary>
          <pre className="text-xs mt-2 overflow-auto max-h-60">
            {JSON.stringify({ attempt, answers }, null, 2)}
          </pre>
        </details>
      )}

      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Detalii Raspunsuri</h2>

        {answers.length === 0 ? (
          <p className="text-gray-500">Nu ai raspuns la nicio intrebare.</p>
        ) : (
          answers.map((item, index) => {
            const isCorrect = item.is_correct
            const correctAnswer = item.question?.correct_answer
            const selectedAnswer = item.selected_answer

            return (
              <div
                key={item.question?.id || index}
                className={`p-4 mb-4 rounded border ${
                  isCorrect
                    ? 'bg-green-50 border-green-300'
                    : 'bg-red-50 border-red-300'
                }`}
              >
                <p className="font-medium mb-3">
                  {index + 1}. {item.question?.question_text}
                </p>

                <div className="ml-4 space-y-1">
                  {['a', 'b', 'c', 'd'].map((opt) => {
                    const isThisCorrect = correctAnswer === opt
                    const isThisSelected = selectedAnswer === opt
                    const optionText =
                      opt === 'a' ? item.question?.option_a :
                      opt === 'b' ? item.question?.option_b :
                      opt === 'c' ? item.question?.option_c :
                      item.question?.option_d

                    let className = 'text-gray-600'
                    if (isThisCorrect) className = 'font-bold text-green-700'
                    if (isThisSelected && !isThisCorrect) className = 'font-bold text-red-700'
                    if (isThisSelected && isThisCorrect) className = 'font-bold text-green-800'

                    return (
                      <p key={opt} className={className}>
                        {opt.toUpperCase()}) {optionText}
                        {isThisCorrect && ' <-- CORECT'}
                        {isThisSelected && !isThisCorrect && ' <-- ales de tine'}
                        {isThisSelected && isThisCorrect && ' (ales de tine, corect)'}
                      </p>
                    )
                  })}
                </div>

                <div className="mt-3 text-sm">
                  {!isCorrect && (
                    <span className="text-red-600 font-medium">
                      Raspunsul tau: {selectedAnswer?.toUpperCase() || 'NICIUNUL'} |
                      Corect: {correctAnswer?.toUpperCase()}
                    </span>
                  )}
                  {isCorrect && (
                    <span className="text-green-600 font-medium">Corect!</span>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>

      <div className="text-center mt-6">
        <Link to="/exams" className="btn btn-primary">
          Inapoi la Examene
        </Link>
      </div>
    </div>
  )
}

export default ExamResult
