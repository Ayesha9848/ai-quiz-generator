import React, { useState } from "react";
import axios from "axios";
import QuizDisplay from "../components/QuizDisplay";

export default function GenerateQuizTab() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleGenerate() {
    setError(null);
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/generate_quiz", { url });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data || e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <input className="input" placeholder="Paste Wikipedia URL (e.g. https://en.wikipedia.org/wiki/Alan_Turing)" value={url} onChange={e=>setUrl(e.target.value)} />
        <div style={{ marginTop:8 }}>
          <button className="btn btn-primary" onClick={handleGenerate}>Generate Quiz</button>
        </div>
      </div>

      {loading && <div className="card">Generating — please wait...</div>}
      {error && <div style={{color:'red'}}>{JSON.stringify(error)}</div>}
      {result && <QuizDisplay data={result} />}
    </div>
  );
}
