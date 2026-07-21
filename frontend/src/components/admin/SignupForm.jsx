import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function SignupForm() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    designation: "",
    assigned_ward: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSignup = async () => {
    setError("");
    setSuccess("");

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Signup failed");
        return;
      }

      setSuccess("Account created successfully!");

      setTimeout(() => {
        navigate("/admin/login");
      }, 1500);

    } catch {
      setError("Unable to connect to server.");
    }
  };

  return (
    <Card className="w-full max-w-md p-6 bg-slate-900 border-slate-800">
      <h1 className="text-2xl font-bold text-white mb-6">
        Create Municipal Account
      </h1>

      <input
        name="name"
        placeholder="Name"
        onChange={handleChange}
        className="w-full mb-3 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
      />

      <input
        name="email"
        type="email"
        placeholder="Email"
        onChange={handleChange}
        className="w-full mb-3 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
      />

      <input
        name="password"
        type="password"
        placeholder="Password"
        onChange={handleChange}
        className="w-full mb-3 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
      />

      <input
        name="designation"
        placeholder="Designation"
        onChange={handleChange}
        className="w-full mb-3 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
      />

      <input
        name="assigned_ward"
        placeholder="Assigned Ward"
        onChange={handleChange}
        className="w-full mb-4 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
      />

      {error && (
        <p className="text-red-500 mb-3">{error}</p>
      )}

      {success && (
        <p className="text-green-500 mb-3">{success}</p>
      )}

      <Button
        className="w-full"
        onClick={handleSignup}
      >
        Create Account
      </Button>
    </Card>
  );
}