import Navbar from '../common/NavBar';

const AdminDashboard = () => {
  return (
    <div>
      <Navbar />
      <div className="dashboard-content">
        <h1>Admin Dashboard</h1>
        {/* Admin-specific components */}
      </div>
    </div>
  );
};

export default AdminDashboard;