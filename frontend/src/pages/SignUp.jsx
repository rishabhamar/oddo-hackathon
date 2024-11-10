import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const SignUp = () => {
  const [role, setRole] = useState('user'); // New state for role selection
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [degree, setDegree] = useState('');
  const [specialization, setSpecialization] = useState('');
  const [experience, setExperience] = useState('');
  const [clinicAddress, setClinicAddress] = useState('');
  
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
  
    // Collect form data based on role
    const payload = {
      email,
      password,
      role,
      ...(role === 'doctor' && { degree, specialization, experience, clinicAddress }),
      ...(role === 'user' && { name }),
    };
  
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
  
    try {
      const response = await fetch('http://localhost:4000/api/user/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
  
      const json = await response.json();
  
      if (response.ok) {
        console.log('Signed up successfully', json);
        navigate('/login');
      } else {
        alert(json.error);
      }
    } catch (error) {
      console.error('Error during sign-up:', error);
      alert('An error occurred during sign-up');
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Sign Up</h2>
      <form onSubmit={handleSignUp}>
        {/* Role selection */}
        <div>
          <label className="form-label">Sign Up As:</label>
          <select 
            className="form-input" 
            value={role} 
            onChange={(e) => setRole(e.target.value)} 
            required
          >
            <option value="user">User</option>
            <option value="doctor">Doctor</option>
          </select>
        </div>

        {/* Common fields */}
        {role === 'user' && (
          <div>
            <label className="form-label">Name:</label>
            <input 
              type="text" 
              className="form-input" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required 
            />
          </div>
        )}
        
        <div>
          <label className="form-label">Email:</label>
          <input 
            type="email" 
            className="form-input" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required 
          />
        </div>
        
        <div>
          <label className="form-label">Password:</label>
          <input 
            type="password" 
            className="form-input" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
        </div>
        
        <div>
          <label className="form-label">Confirm Password:</label>
          <input 
            type="password" 
            className="form-input" 
            value={confirmPassword} 
            onChange={(e) => setConfirmPassword(e.target.value)} 
            required 
          />
        </div>

        {/* Doctor-specific fields */}
        {role === 'doctor' && (
          <>
            <div>
              <label className="form-label">Degree:</label>
              <input 
                type="text" 
                className="form-input" 
                value={degree} 
                onChange={(e) => setDegree(e.target.value)} 
                required 
              />
            </div>
            <div>
              <label className="form-label">Specialization:</label>
              <input 
                type="text" 
                className="form-input" 
                value={specialization} 
                onChange={(e) => setSpecialization(e.target.value)} 
                required 
              />
            </div>
            <div>
              <label className="form-label">Experience (in years):</label>
              <input 
                type="number" 
                className="form-input" 
                value={experience} 
                onChange={(e) => setExperience(e.target.value)} 
                required 
              />
            </div>
            <div>
              <label className="form-label">Clinic Address:</label>
              <input 
                type="text" 
                className="form-input" 
                value={clinicAddress} 
                onChange={(e) => setClinicAddress(e.target.value)} 
                required 
              />
            </div>
          </>
        )}

        <button type="submit" className="form-button">Sign Up</button>
      </form>
      <p className="form-link">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
};

export default SignUp;
