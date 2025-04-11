import { useState } from 'react';
import axios from 'axios';

function LoanApplication() {
  const [amount, setAmount] = useState('');
  const [duration, setDuration] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/loan/apply', { amount, loan_duration: duration }, { withCredentials: true });
      setMessage('Loan application submitted!');
      // ✅ Clear the form
      setAmount('');
      setDuration('');
    } catch (error) {
      setMessage(error.response?.data?.error || 'Application failed');
    }
  };

  return (
    <div className="loan-application">
      <h3>Apply for Loan</h3>
      <form onSubmit={handleSubmit}>
        {/* Form fields */}
        <div>
          <label>Amount:</label>
          <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        </div>
        <div>
          <label>Duration (in months):</label>
          <input
          type="number"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          required
        />
        </div>
        <button type="submit">Apply</button>
        {message && <div>{message}</div>}
      </form>
    </div>
  );
}

export default LoanApplication