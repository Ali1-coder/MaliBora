import { useAuth } from '../context/AuthContext';

function Dashboard() {
  const { currentUser, logout } = useAuth();

  if (!currentUser) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-gray-600 text-lg">Loading user info...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="flex flex-col sm:flex-row justify-between items-center bg-white p-4 rounded-xl shadow mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">
          Welcome, {currentUser.username}
        </h1>
        <button
          onClick={logout}
          className="mt-4 sm:mt-0 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
        >
          Logout
        </button>
      </header>

      {currentUser.role === 'customer' && (
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-4 text-blue-600">Account Overview</h2>
          <p className="text-gray-700 mb-2">
            <span className="font-semibold">Account Number:</span> {currentUser.account_number}
          </p>
          <p className="text-gray-700">
            <span className="font-semibold">Balance:</span> ${currentUser.savings_balance}
          </p>
        </div>
      )}

      {currentUser.role === 'admin' && (
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold text-green-700 mb-4">Admin Controls</h2>
          <p className="text-gray-600">Access admin tools and user management features here.</p>
          {/* Add your admin tools/components here */}
        </div>
      )}

      {currentUser.role === 'staff' && (
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold text-purple-700 mb-4">Staff Portal</h2>
          <p className="text-gray-600">Manage customer support, view logs, and more.</p>
          {/* Add your staff tools/components here */}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
