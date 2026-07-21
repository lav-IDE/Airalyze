import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function LoginForm() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        setError("Incorrect email or password");
        return;
      }

      const data = await response.json();

      localStorage.setItem("token", data.access_token);

      navigate("/admin/dashboard");
    } catch (err) {
      setError("Unable to connect to server.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <Card className="w-full max-w-md p-6 bg-slate-900 border-slate-800">
        <h1 className="text-2xl font-bold text-white mb-6">
          Municipal Authority Login
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-4 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 rounded-lg border border-slate-700 bg-slate-800 p-3 text-white"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && (
          <p className="text-red-500 text-sm mb-4">{error}</p>
        )}

        <Button
          className="w-full"
          onClick={handleLogin}
        >
          Login
        </Button>
        <Button
  variant="outline"
  className="w-full mt-3"
  onClick={() => navigate("/signup")}
>
  Create Account
</Button>
      </Card>
    </div>
  );
}