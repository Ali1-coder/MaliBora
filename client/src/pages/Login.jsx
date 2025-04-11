import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  try {
    await login(email, password);
    navigate('/');
  } catch (err) {
    setError(err.response?.data?.error || 'Login failed');
  }
  setLoading(false);
};

  

  return (
    <div className="max-w-sm mx-auto mt-20 p-6 bg-white rounded shadow">
  <h2 className="text-xl font-semibold mb-4">Bank Login</h2>
  <form onSubmit={handleSubmit} className="space-y-4">
    <div>
      <label className="block text-sm font-medium">Email:</label>
      <input
        type="email"
        className="w-full border px-3 py-2 rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
    </div>
    <div>
      <label className="block text-sm font-medium">Password:</label>
      <input
        type="password"
        className="w-full border px-3 py-2 rounded"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
    </div>
    {error && <div className="text-red-500 text-sm">{error}</div>}
    <button
      type="submit"
      className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
    >
      {loading ? 'Logging in...' : 'Login'}
    </button>
  </form>
</div>

  );
}

export default Login