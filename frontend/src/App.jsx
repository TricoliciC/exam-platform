import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ExamList from './pages/ExamList'
import ExamDetail from './pages/ExamDetail'
import ExamTest from './pages/ExamTest'
import ExamResult from './pages/ExamResult'
import AdminDashboard from './pages/AdminDashboard'
import AdminCategories from './pages/AdminCategories'
import AdminExams from './pages/AdminExams'
import AdminSettings from './pages/AdminSettings'
import AdminUsers from './pages/AdminUsers'
import UserAttempts from './pages/UserAttempts'

function App() {
  const [user, setUser] = useState(null)
  const [siteSettings, setSiteSettings] = useState(null)

  useEffect(() => {
    // Check for stored token
    const token = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (token && storedUser) {
      setUser(JSON.parse(storedUser))
    }
    
    // Fetch site settings
    fetchSiteSettings()
  }, [])

  const fetchSiteSettings = async () => {
    try {
      const response = await fetch('/api/user/settings')
      const data = await response.json()
      setSiteSettings(data.settings)
    } catch (error) {
      console.error('Error fetching site settings:', error)
    }
  }

  const login = (userData, token) => {
    setUser(userData)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar user={user} siteSettings={siteSettings} onLogout={logout} />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home siteSettings={siteSettings} />} />
            <Route path="/login" element={<Login onLogin={login} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/exams" element={<ExamList user={user} />} />
            <Route path="/exams/:id" element={<ExamDetail user={user} />} />
            <Route path="/exams/:id/test" element={<ExamTest user={user} />} />
            <Route path="/exams/:id/result/:attemptId" element={<ExamResult user={user} />} />
            <Route path="/attempts" element={<UserAttempts user={user} />} />
            <Route 
              path="/admin" 
              element={user?.is_admin ? <AdminDashboard /> : <Navigate to="/" />} 
            />
            <Route 
              path="/admin/categories" 
              element={user?.is_admin ? <AdminCategories /> : <Navigate to="/" />} 
            />
            <Route 
              path="/admin/exams" 
              element={user?.is_admin ? <AdminExams /> : <Navigate to="/" />} 
            />
            <Route 
              path="/admin/settings" 
              element={user?.is_admin ? <AdminSettings /> : <Navigate to="/" />} 
            />
            <Route 
              path="/admin/users" 
              element={user?.is_admin ? <AdminUsers /> : <Navigate to="/" />} 
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
