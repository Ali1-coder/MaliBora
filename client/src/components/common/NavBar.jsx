import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div>Bank System</div>
      {user && (
        <div className="nav-right">
          <span className={`role-badge ${user.role}`}>
            {user.role.toUpperCase()}
          </span>
          <span className="username">{user.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;