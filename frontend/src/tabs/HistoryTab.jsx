import React, { useEffect, useState } from "react";
import axios from "axios";
import QuizDisplay from "../components/QuizDisplay";

export default function HistoryTab() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(()=>{ fetchHistory() }, []);

  async function fetchHistory() {
    const res = await axios.get("http://localhost:8000/history");
    setItems(res.data || []);
  }

  async function openDetails(id) {
    const res = await axios.get(`http://localhost:8000/quiz/${id}`);
    setSelected(res.data);
  }

  return (
    <div>
      <div className="card" style={{marginBottom:12}}>
        <table className="table">
          <thead><tr><th>ID</th><th>Title</th><th>URL</th><th>Date</th><th></th></tr></thead>
          <tbody>
            {items.map(it=>(
              <tr key={it.id}>
                <td>{it.id}</td>
                <td>{it.title}</td>
                <td style={{maxWidth:300, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap"}}>{it.url}</td>
                <td>{new Date(it.date_generated).toLocaleString()}</td>
                <td><button className="btn" onClick={()=>openDetails(it.id)}>Details</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && <div className="card"><button className="btn" onClick={()=>setSelected(null)}>Close</button><QuizDisplay data={selected} /></div>}
    </div>
  );
}
