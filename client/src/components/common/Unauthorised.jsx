import { useNavigate } from 'react-router-dom';

const Unauthorized = () => {
  const navigate = useNavigate();

  return (
    <div className="unauthorized-container">
      <h1>403 - Forbidden</h1>
      <p>You don't have permission to access this page.</p>
      <button 
        onClick={() => navigate(-1)}
        className="go-back-btn"
      >
        Go Back
      </button>
      <p>or</p>
      <button
        onClick={() => navigate('/dashboard')}
        className="dashboard-btn"
      >
        Return to Dashboard
      </button>
    </div>
  );
};

export default Unauthorized;