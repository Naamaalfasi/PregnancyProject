import React from "react";

function DynamicInputList({ label, values, setValues, placeholder = "" }) {
  const addField = () => setValues([...values, ""]);
  const updateField = (idx, value) => {
    const newArr = [...values];
    newArr[idx] = value;
    setValues(newArr);
  };
  const removeField = (idx) => {
    const newArr = values.filter((_, i) => i !== idx);
    setValues(newArr);
  };

  return (
    <>
      <label>{label}</label>
      {values.map((val, idx) => (
        <div
          key={idx}
          style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
        >
          <input
            type="text"
            value={val}
            onChange={(e) => updateField(idx, e.target.value)}
            className="login-input"
            style={{ flex: 1 }}
            placeholder={placeholder}
          />
          {values.length > 1 && (
            <button
              type="button"
              onClick={() => removeField(idx)}
              className="plus-minus-btn"
            >
              –
            </button>
          )}
          {idx === values.length - 1 && (
            <button type="button" onClick={addField} className="plus-minus-btn">
              +
            </button>
          )}
        </div>
      ))}
    </>
  );
}

export default DynamicInputList;
