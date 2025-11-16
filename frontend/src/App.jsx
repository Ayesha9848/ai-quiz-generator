import React, { useState } from "react";
import GenerateQuizTab from "./tabs/GenerateQuizTab";
import HistoryTab from "./tabs/HistoryTab";

export default function App() {
  const [tab, setTab] = useState("generate");
  return (
    <div className="container">
      <div className="header">
        <h1>DeepKlarity — AI Wiki Quiz Generator</h1>
        <div>
          <button className={`btn ${tab==="generate" ? "btn-primary" : ""}`} onClick={()=>setTab("generate")}>Generate</button>
          <button className={`btn ${tab==="history" ? "btn-primary" : ""}`} style={{marginLeft:8}} onClick={()=>setTab("history")}>History</button>
        </div>
      </div>
      {tab === "generate" ? <GenerateQuizTab /> : <HistoryTab />}
    </div>
  );
}
