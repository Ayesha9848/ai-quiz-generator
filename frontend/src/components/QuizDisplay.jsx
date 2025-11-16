import React from "react";

export default function QuizDisplay({ data }) {
  if (!data) return null;
  return (
    <div style={{display:'grid', gap:12}}>
      <div className="card">
        <h2 style={{margin:0}}>{data.title}</h2>
        <p style={{marginTop:8}}>{data.summary}</p>
        <div style={{marginTop:6}}>Related: {data.related_topics?.join(", ")}</div>
      </div>

      <div style={{display:'grid', gap:8}}>
        {data.quiz?.map((q, i) => (
          <div key={i} className="card">
            <div style={{fontWeight:600}}>Q{i+1}. {q.question}</div>
            <ol style={{marginTop:8, marginLeft:18}}>
              {q.options.map((op, idx) => <li key={idx}>{op}</li>)}
            </ol>
            <div style={{marginTop:8, color:'#6b7280', fontSize:13}}>Answer: {q.answer} • Difficulty: {q.difficulty}</div>
            <div style={{marginTop:6}}>{q.explanation}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
