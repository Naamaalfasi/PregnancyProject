import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./Login.css";
import DynamicInputList from "../components/DynamicInputList";

function ProfileSetup() {
  const location = useLocation();
  const navigate = useNavigate();
  const userId = location.state?.userId;

  const [dateOfBirth, setDateOfBirth] = useState("");
  const [lmpDate, setLmpDate] = useState("");
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [bloodType, setBloodType] = useState("");
  const [medicalConditions, setMedicalConditions] = useState([""]);
  const [allergies, setAllergies] = useState([""]);
  const [medications, setMedications] = useState([""]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          date_of_birth: dateOfBirth,
          lmp_date: lmpDate,
          height: parseFloat(height),
          weight: parseFloat(weight),
          blood_type: bloodType,
          medical_conditions: medicalConditions.filter(Boolean),
          allergies: allergies.filter(Boolean),
          medications: medications.filter(Boolean),
        }),
      });
      if (response.ok) {
        navigate("/dashboard");
      } else {
        const data = await response.json();
        setError(data.detail || "שגיאה בעדכון הפרופיל");
      }
    } catch (err) {
      setError("שגיאת רשת");
    }
    setLoading(false);
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>רגע לפני שנמשיך, נשמח להכיר אותך קצת יותר</h2>

        <div className="form-group">
          <label htmlFor="dateOfBirth">תאריך לידה</label>
          <input
            id="dateOfBirth"
            type="date"
            value={dateOfBirth}
            onChange={(e) => setDateOfBirth(e.target.value)}
            className="login-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="lmpDate">תאריך וסת אחרונה</label>
          <input
            id="lmpDate"
            type="date"
            value={lmpDate}
            onChange={(e) => setLmpDate(e.target.value)}
            className="login-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="height">גובה (ס"מ)</label>
          <input
            id="height"
            type="number"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            className="login-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="weight">משקל (ק"ג)</label>
          <input
            id="weight"
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            className="login-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="bloodType">סוג דם</label>
          <input
            id="bloodType"
            type="text"
            value={bloodType}
            onChange={(e) => setBloodType(e.target.value)}
            className="login-input"
            required
          />
        </div>

        <div className="form-group">
          <DynamicInputList
            label="מחלות רקע:"
            values={medicalConditions}
            setValues={setMedicalConditions}
            placeholder="הקלד/י מחלה"
          />
        </div>

        <div className="form-group">
          <DynamicInputList
            label="אלרגיות:"
            values={allergies}
            setValues={setAllergies}
            placeholder="הקלד/י אלרגיה"
          />
        </div>

        <div className="form-group">
          <DynamicInputList
            label="תרופות:"
            values={medications}
            setValues={setMedications}
            placeholder="הקלד/י תרופה"
          />
        </div>

        <button type="submit" disabled={loading} className="login-button">
          {loading ? "שומר..." : "המשך"}
        </button>
        {error && <div className="login-error">{error}</div>}
      </form>
    </div>
  );
}

export default ProfileSetup;
