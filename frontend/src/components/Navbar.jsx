import { Link } from 'react-router-dom'

function Navbar({ user, siteSettings, onLogout }) {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            {siteSettings?.logo_url ? (
              <img src={siteSettings.logo_url} alt="Logo" className="h-10" />
            ) : (
              siteSettings?.site_name || 'Platformă de Testare'
            )}
          </Link>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-gray-600">Salut, {user.username}</span>
                {user.is_admin && (
                  <Link to="/admin" className="text-blue-600 hover:text-blue-800">
                    Admin
                  </Link>
                )}
                <Link to="/attempts" className="text-blue-600 hover:text-blue-800">
                  Încercările mele
                </Link>
                <button
                  onClick={onLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Înregistrare
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
