import { useEffect, useState } from "react";
import { checkStatus, getResult } from "../api/api";
import ResultView from "./ResultView";

export default function StatusLoader({ jobId }) {
  const [status, setStatus] = useState("Checking...");
  const [result, setResult] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await checkStatus(jobId);
        setStatus(res.data.status);

        if (res.data.status === "SUCCESS") {
          const finalRes = await getResult(jobId);
          setResult(finalRes.data.result);
          clearInterval(interval);
        }

        if (res.data.status === "FAILURE") {
          setResult({
            error: res.data.detail || "Task failed",
          });
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Status: {status}</h3>

      {!result && (
        <div style={{ fontSize: "15px", opacity: 0.7 }}>
          Waiting for task to complete...
        </div>
      )}

      {result && <ResultView result={result} />}
    </div>
  );
}
