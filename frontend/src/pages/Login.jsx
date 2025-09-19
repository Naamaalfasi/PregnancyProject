import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import EyeToggleInput from "../components/icons/EyeToggleInput";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // שליחת בקשה לשרת (בהמשך תעדכני את ה-API שיקבל אימייל)
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (response.ok && data.success) {
        localStorage.setItem("token", data.token); // או user_id, לפי מה שתחליטי
        navigate("/dashboard"); // לזכור להחליף את הנתיב
      } else {
        setError(data.message || "אימייל או סיסמה שגויים");
      }
    } catch (err) {
      setError("שגיאת רשת");
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>התחברות</h2>
        <input
          type="email"
          placeholder="אימייל"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
        <button type="submit" disabled={loading} className="login-button">
          {loading ? "מתחבר..." : "התחבר"}
        </button>
        <button
          type="button"
          onClick={() => navigate("/register")}
          className="login-register-button"
        >
          אין לך חשבון? להרשמה
        </button>
        {error && <div className="login-error">{error}</div>}
      </form>
    </div>
  );
}

export default Login;
