import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import "./Login.css";

function App() {
  const [guardId, setGuardId] = useState("");
  const [mobileNumber, setMobileNumber] = useState("");
  const [message, setMessage] = useState("");
  const [color, setColor] = useState("");
  const navigate = useNavigate(); // Initialize useNavigate

  const handleLogin = async (e) => {
    e.preventDefault();

    const data = {
      emp_id: guardId.trim(), // Use emp_id instead of guardId
      mobile_number: mobileNumber.trim(), // Use mobile_number instead of mobileNumber
    };

    try {
      const response = await fetch(
        "https://web-production-5485.up.railway.app/verify_guard",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.message === "Verified") {
          localStorage.setItem('mobileNumber', mobileNumber);
          setColor("#228B22");
          setMessage("Login successful!");

          // useEffect(() => {
          fetch(`https://web-production-5485.up.railway.app/guards/${mobileNumber}`) // Replace with actual API URL
            .then((response) => {
              if (!response.ok) {
                throw new Error("Network response was not ok");
              }
              return response.json();
            })
            .then((data) => {
              localStorage.setItem("employeeData", JSON.stringify(data));
            })
            .catch((error) => {
              setError(error.message);
            });
          // }, []); // Empty dependency array to run only once when component mounts

          setTimeout(() => {
            navigate("/List");
          }, 1000); // Replace '/dashboard' with your desired path
        } else {
          setMessage("Login failed. Invalid Guard ID or Mobile Number.");
        }
      } else {
        setMessage("Login failed. Server error.");
      }
    } catch (error) {
      setColor("#B22222");
      setMessage("Login failed. Network error.");
    }
  };

  const handleSendOtp = () => {
    // Functionality to send OTP can be added here
    setMessage("OTP sent to the provided mobile number.");
  };

  return (
    <>
      <div className="container">
        <img className="logo" src="/logo.png" alt="Logo" />
        <h1>Account Login</h1>
        <form className="input" onSubmit={handleLogin}>
          <div className="fill">
            <div className="guard-id">
              <label htmlFor="guardId">Guard ID:</label>
              <input
                type="text"
                id="guardId"
                name="guardId"
                value={guardId}
                onChange={(e) => setGuardId(e.target.value)}
                required
              />
            </div>
            <div className="mobile-number">
              <label htmlFor="mobileNumber">Mobile Number:</label>
              <input
                type="text"
                id="mobileNumber"
                name="mobileNumber"
                value={mobileNumber}
                onChange={(e) => setMobileNumber(e.target.value)}
                required
              />
            </div>
          </div>
          <button type="submit" className="button">
            Login
          </button>
          <button type="button" className="button" onClick={handleSendOtp}>
            Send OTP
          </button>
          <p className="resend">
            <a href="#" onClick={handleSendOtp}>
              Resend OTP
            </a>
          </p>
        </form>
        {message && <p className="message" style={{ color }}>{message}</p>}
      </div>
    </>
  );
}

export default App;