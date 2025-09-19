import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import EyeToggleInput from "../components/icons/EyeToggleInput";

function Register() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [passwordMatchError, setPasswordMatchError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setPasswordMatchError("");

    if (password !== confirmPassword) {
      setPasswordMatchError("הסיסמאות אינן זהות");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, password }),
      });
      const data = await response.json();
      if (response.ok) {
        // נווטי למסך השאלון/השלמת פרופיל
        navigate("/profile-setup", { state: { userId: data.user_id } });
      } else {
        setError(data.detail || "שגיאה בהרשמה");
      }
    } catch (err) {
      setError("שגיאת רשת");
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>הרשמה</h2>
        <input
          type="email"
          placeholder="אימייל"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="login-input"
        />
        <input
          type="text"
          placeholder="שם מלא"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="login-input"
        />
        <EyeToggleInput
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          show={showPassword}
          setShow={setShowPassword}
          placeholder="סיסמה"
          required
        />
        <EyeToggleInput
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          show={showConfirmPassword}
          setShow={setShowConfirmPassword}
          placeholder="אימות סיסמה"
          required
        />
        <button type="submit" disabled={loading} className="login-button">
          {loading ? "נרשם..." : "הרשמה"}
        </button>
        <button
          type="button"
          onClick={() => navigate("/login")}
          className="login-register-button"
        >
          כבר יש לך חשבון? התחבר/י
        </button>
        {passwordMatchError && (
          <div className="login-error">{passwordMatchError}</div>
        )}
        {error && <div className="login-error">{error}</div>}
      </form>
    </div>
  );
}

export default Register;
