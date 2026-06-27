import { Link } from 'react-router-dom'

function AdminDashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Panou Admin</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link to="/admin/categories" className="card hover:shadow-lg transition-shadow">
          <h2 className="text-xl font-bold mb-2">Categorii</h2>
          <p className="text-gray-600">Gestionează categoriile de examene</p>
        </Link>
        
        <Link to="/admin/exams" className="card hover:shadow-lg transition-shadow">
          <h2 className="text-xl font-bold mb-2">Examene</h2>
          <p className="text-gray-600">Încarcă și gestionează examenele</p>
        </Link>
        
        <Link to="/admin/settings" className="card hover:shadow-lg transition-shadow">
          <h2 className="text-xl font-bold mb-2">Setări Site</h2>
          <p className="text-gray-600">Modifică setările platformei</p>
        </Link>

        <Link to="/admin/users" className="card hover:shadow-lg transition-shadow">
          <h2 className="text-xl font-bold mb-2">Utilizatori</h2>
          <p className="text-gray-600">Gestionează conturile utilizatorilor</p>
        </Link>
      </div>

      <div className="card mt-6">
        <h2 className="text-xl font-bold mb-4">Instrucțiuni</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-600">
          <li>Creează categorii pentru a organiza examenele</li>
          <li>Încarcă fișiere PDF cu întrebări și variante de răspuns</li>
          <li>Formatul PDF așteptat: întrebare urmată de opțiunile a), b), c), d) și răspunsul corect marcat</li>
          <li>Modifică setările site-ului (nume, logo, mesaj de bun venit)</li>
          <li>Gestionează utilizatorii (editare, ștergere, resetare parolă)</li>
        </ul>
      </div>
    </div>
  )
}

export default AdminDashboard
