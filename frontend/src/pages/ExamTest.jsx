import { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'

function ExamTest({ user }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { attemptId, questions: initialQuestions } = location.state || { attemptId: null, questions: [] }

  const [questions] = useState(initialQuestions)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [attemptCount, setAttemptCount] = useState({})

  useEffect(() => {
    if (!attemptId || !questions.length) {
      navigate(`/exams/${id}`)
    }
  }, [attemptId, questions, id, navigate])

  const handleAnswer = (questionId, answer) => {
    // Increment attempt counter for this question
    setAttemptCount((prev) => ({
      ...prev,
      [questionId]: (prev[questionId] || 0) + 1
    }))
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer
    }))
  }

  const submitExam = async () => {
    try {
      const token = localStorage.getItem('token')
      const answersArray = Object.entries(answers).map(([qid, selectedAnswer]) => ({
        question_id: parseInt(qid),
        selected_answer: selectedAnswer
      }))

      if (answersArray.length === 0) {
        alert('Nu ai raspuns la nicio intrebare!')
        return
      }

      const response = await fetch(`/api/exams/attempts/${attemptId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ answers: answersArray })
      })

      const data = await response.json()
      if (response.ok) {
        navigate(`/exams/${id}/result/${attemptId}`)
      } else {
        alert('Eroare la trimitere: ' + (data.error || 'necunoscuta'))
      }
    } catch (error) {
      console.error('Error submitting exam:', error)
      alert('Eroare retea: ' + error.message)
    }
  }

  if (!questions.length) {
    return <div className="text-center py-8">Încărcare...</div>
  }

  const question = questions[currentQuestion]
  const answeredCount = Object.keys(answers).length
  const selectedAnswer = answers[question.id]
  const isCorrect = selectedAnswer ? selectedAnswer === question.correct_answer : null

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Test: Întrebarea {currentQuestion + 1} din {questions.length}</h1>
        <div className="text-lg font-medium text-gray-600">
          Răspunse: {answeredCount} / {questions.length}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-medium mb-6">{question.question_text}</h2>

        <div className="space-y-3">
          {['a', 'b', 'c', 'd'].map((option) => {
            const isSelected = selectedAnswer === option
            const isThisCorrect = option === question.correct_answer
            let borderClass = 'border-gray-300 hover:bg-gray-50'
            if (isSelected && isThisCorrect) borderClass = 'border-green-500 bg-green-50'
            else if (isSelected && !isThisCorrect) borderClass = 'border-red-500 bg-red-50'
            else if (!isSelected && isThisCorrect && selectedAnswer) borderClass = 'border-green-300 bg-green-50/50'

            return (
              <label
                key={option}
                className={`flex items-center p-4 border-2 rounded cursor-pointer transition-colors ${borderClass}`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={option}
                  checked={isSelected}
                  onChange={() => handleAnswer(question.id, option)}
                  className="mr-4"
                />
                <span className="font-bold mr-2">{option.toUpperCase()}.</span>
                <span className="flex-1">
                  {option === 'a' && question.option_a}
                  {option === 'b' && question.option_b}
                  {option === 'c' && question.option_c}
                  {option === 'd' && question.option_d}
                </span>
                {isThisCorrect && selectedAnswer && (
                  <span className="ml-2 text-green-600 font-bold text-lg">✓</span>
                )}
                {isSelected && !isThisCorrect && (
                  <span className="ml-2 text-red-500 font-bold text-lg">✗</span>
                )}
              </label>
            )
          })}
        </div>

        {/* Feedback imediat */}
        {selectedAnswer && (
          <div className={`mt-4 p-4 rounded-lg border-2 ${
            isCorrect
              ? 'bg-green-100 border-green-400'
              : 'bg-red-100 border-red-400'
          }`}>
            <div className="flex items-center gap-2">
              <span className={`text-lg font-bold ${
                isCorrect ? 'text-green-700' : 'text-red-700'
              }`}>
                {isCorrect ? '✓ CORECT!' : '✗ GRESIT!'}
              </span>
              {!isCorrect && (
                <span className="text-red-600">
                  Răspunsul corect este: <strong>{question.correct_answer.toUpperCase()}</strong>
                </span>
              )}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              Ai raspuns la aceasta intrebare de <strong>{attemptCount[question.id] || 1}</strong> ori
            </div>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <button
            onClick={() => setCurrentQuestion((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestion === 0}
            className="btn btn-secondary"
          >
            ← Intrebarea anterioara
          </button>

          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={() => {
                if (confirm(`Ai raspuns la ${answeredCount} din ${questions.length} intrebari. Trimit acum?`)) {
                  submitExam()
                }
              }}
              className="btn btn-success"
            >
              Trimite Testul ({answeredCount}/{questions.length})
            </button>
          ) : (
            <button
              onClick={() => setCurrentQuestion((prev) => Math.min(questions.length - 1, prev + 1))}
              className="btn btn-primary"
            >
              Intrebarea urmatoare →
            </button>
          )}
        </div>
      </div>

      <div className="mt-6">
        <h3 className="font-medium mb-3">Progres intrebari:</h3>
        <div className="flex flex-wrap gap-2">
          {questions.map((q, index) => {
            const ans = answers[q.id]
            return (
              <button
                key={q.id}
                onClick={() => setCurrentQuestion(index)}
                className={`px-3 py-1.5 rounded text-sm font-medium ${
                  currentQuestion === index
                    ? 'bg-blue-500 text-white'
                    : ans !== undefined
                    ? ans === q.correct_answer
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {index + 1}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ExamTest
