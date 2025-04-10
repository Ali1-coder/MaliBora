import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import AdminDashboard from './components/dashboard/AdminDashboard';
// import StaffDashboard from './components/dashboard/StaffDashboard';
// import CustomerDashboard from './components/dashboard/CustomerDashboard';
import Unauthorized from './components/common/Unauthorized';

function App() {
  return (
    
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          
          <Route element={<PrivateRoute requiredRole="admin" />}>
            <Route path="/admin/*" element={<AdminDashboard />} />
          </Route>
          
          {/* <Route element={<PrivateRoute requiredRole="staff" />}>
            <Route path="/staff/*" element={<StaffDashboard />} />
          </Route> */}
          
          {/* <Route element={<PrivateRoute />}>
            <Route path="/dashboard/*" element={<CustomerDashboard />} />
          </Route> */}
          
          {/* <Route path="/" element={<Navigate to="/dashboard" />} /> */}
        </Routes>
      </AuthProvider>
    
  );
}

export default App;