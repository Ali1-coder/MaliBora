
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminCreateUser from './pages/AdminCreateUser';
// import Loans from './pages/Loans';
// import Transactions from './pages/Transactions';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/admin/create-user" element={<AdminRoute><AdminCreateUser /></AdminRoute>} />
          {/* <Route path="/loans" element={<CustomerRoute><Loans /></CustomerRoute>} /> */}
          {/* <Route path="/transactions" element={<CustomerRoute><Transactions /></CustomerRoute>} /> */}
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

function PrivateRoute({ children }) {
  const { currentUser } = useAuth();
  return currentUser ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { currentUser } = useAuth();
  return currentUser?.role === 'admin' ? children : <Navigate to="/" />;
}

function CustomerRoute({ children }) {
  const { currentUser } = useAuth();
  return currentUser?.role === 'customer' ? children : <Navigate to="/" />;
}

export default App;
