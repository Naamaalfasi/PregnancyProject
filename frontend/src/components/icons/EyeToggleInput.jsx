import React from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";

function EyeToggleInput({
  value,
  onChange,
  show,
  setShow,
  placeholder,
  ...props
}) {
  return (
    <div className="login-password-wrapper">
      <input
        type={show ? "text" : "password"}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="login-input"
        {...props}
      />
      <span
        onClick={() => setShow((prev) => !prev)}
        className="login-eye-icon"
        tabIndex={0}
        role="button"
        aria-label={show ? "הסתר סיסמה" : "הצג סיסמה"}
      >
        {show ? <FiEyeOff /> : <FiEye />}
      </span>
    </div>
  );
}

export default EyeToggleInput;
