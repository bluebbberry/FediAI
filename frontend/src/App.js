import React, { useState, useEffect } from "react";

export default function HyperloopUI() {
  const [prompt, setPrompt] = useState("");
  const [tasks, setTasks] = useState([]);
  const [routingOption, setRoutingOption] = useState("same_hashtag");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);

  const sendPrompt = async () => {
    setStatus("Sending prompt...");
    const requestData = {
      tasks,
      value: prompt,
      options: { routing: routingOption },
    };

    try {
      const response = await fetch("http://localhost:5000/send_prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });
      const data = await response.json();
      setStatus("Waiting for results...");
    } catch (error) {
      setStatus("Error sending prompt");
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const response = await fetch("http://localhost:5000/get_result");
        const data = await response.json();
        if (data.result) {
          setResult(data.result);
          setStatus("Completed");
        }
      } catch (error) {
        console.error("Error fetching result:", error);
      }
    };

    if (status === "Waiting for results...") {
      const interval = setInterval(fetchResult, 5000);
      return () => clearInterval(interval);
    }
  }, [status]);

  const addTask = (task) => {
    if (!tasks.includes(task)) {
      setTasks([...tasks, task]);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "500px", margin: "0 auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "10px" }}>Hyperloop AI Task Designer</h1>
      <textarea
        style={{ width: "100%", padding: "10px", marginBottom: "10px", border: "1px solid #ccc", borderRadius: "5px" }}
        placeholder="Enter your prompt here..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <div style={{ marginBottom: "10px" }}>
        <label>Routing Option: </label>
        <select value={routingOption} onChange={(e) => setRoutingOption(e.target.value)}>
          <option value="same_hashtag">Same Hashtag</option>
          <option value="local_routing_table">Use Local Prompt Routing Table</option>
        </select>
      </div>
      <div style={{ marginBottom: "10px" }}>
        <label>Add Task: </label>
        <button onClick={() => addTask("uppercaser")} style={{ marginRight: "5px" }}>Uppercaser</button>
        <button onClick={() => addTask("translation")} style={{ marginRight: "5px" }}>Translation</button>
      </div>
      <p>Selected Tasks: {tasks.join(", ") || "None"}</p>
      <button
        onClick={sendPrompt}
        style={{ width: "100%", padding: "10px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}>
        Send to Hyperloop
      </button>
      {status && <p style={{ marginTop: "10px", color: "#555" }}>{status}</p>}
      {result && (
        <div style={{ marginTop: "10px", padding: "10px", border: "1px solid #ccc", borderRadius: "5px", backgroundColor: "#f9f9f9" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "bold" }}>Final Result</h2>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}
