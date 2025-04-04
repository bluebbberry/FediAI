import React, { useState, useEffect } from "react";

export default function FediAIApp() {
  const [view, setView] = useState("start"); // start | select | chat
  const [selectedHashtag, setSelectedHashtag] = useState(null);

  const [prompt, setPrompt] = useState("");
  const [tasks, setTasks] = useState([]);
  const [routingOption, setRoutingOption] = useState("same_hashtag");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [processingLoops, setProcessingLoops] = useState([]);

  const trendingHashtags = ["#whattocook", "#diyideas", "#learnai", "#promptsharing"];

  const sendPrompt = async () => {
    setStatus("Sending prompt...");
    setProcessingLoops([]);

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
      await response.json();
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
          setProcessingLoops(data.loops || []);
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

  // VIEWS
  if (view === "start") {
    return (
      <div style={{ textAlign: "center", padding: "100px", fontFamily: "Arial, sans-serif" }}>
        <h1 style={{ fontSize: "48px", fontWeight: "bold", color: "#4B0082" }}>FediAI</h1>
        <button
          onClick={() => setView("select")}
          style={{ marginTop: "40px", padding: "10px 20px", fontSize: "18px", borderRadius: "8px", backgroundColor: "#4B0082", color: "white", border: "none", cursor: "pointer" }}>
          Enter
        </button>
      </div>
    );
  }

  if (view === "select") {
    return (
      <div style={{ padding: "40px", fontFamily: "Arial, sans-serif", textAlign: "center" }}>
        <h2 style={{ fontSize: "32px", marginBottom: "20px" }}>Trending AI Hashtags</h2>
        {trendingHashtags.map((tag) => (
          <button
            key={tag}
            onClick={() => {
              setSelectedHashtag(tag);
              setView("chat");
            }}
            style={{ display: "block", margin: "10px auto", padding: "12px 24px", fontSize: "18px", borderRadius: "8px", backgroundColor: "#eee", border: "1px solid #ccc", cursor: "pointer" }}>
            {tag}
          </button>
        ))}
      </div>
    );
  }

  // CHAT VIEW
  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "10px" }}>
        Chat: {selectedHashtag}
      </h1>
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
        Send to Fediverse
      </button>
      {status && <p style={{ marginTop: "10px", color: "#555" }}>{status}</p>}

      {processingLoops.length > 0 && (
        <div style={{ marginTop: "10px", padding: "10px", border: "1px solid #ccc", borderRadius: "5px", backgroundColor: "#f9f9f9" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "bold" }}>Processing Loops</h2>
          <ul>
            {processingLoops.map((loop, index) => (
              <li key={index}>{loop}</li>
            ))}
          </ul>
        </div>
      )}

      {result && (
        <div style={{ marginTop: "10px", padding: "10px", border: "1px solid #ccc", borderRadius: "5px", backgroundColor: "#f9f9f9" }}>
          <h2 style={{ fontSize: "16px", fontWeight: "bold" }}>Final Result</h2>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}
