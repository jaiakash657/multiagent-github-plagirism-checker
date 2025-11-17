import { useState } from "react";
import { analyzeRepo, checkStatus, getResult } from "../api/api";

export default function Analyzer() {
    const [repoUrl, setRepoUrl] = useState("");
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {
        console.log("Analyze button clicked");

        if (!repoUrl) {
            alert("Enter a Repo URL");
            return;
        }

        try {
            const response = await analyzeRepo(repoUrl);
            console.log("Analyze API response:", response);

            setJobId(response.job_id);
            setStatus("Queued");

            // Poll for status
            pollStatus(response.job_id);
        } catch (err) {
            console.error(err);
        }
    };

    const pollStatus = (job) => {
        const interval = setInterval(async () => {
            const statusRes = await checkStatus(job);
            console.log("Status:", statusRes);

            setStatus(statusRes.status);

            if (statusRes.status === "SUCCESS") {
                clearInterval(interval);
                const data = await getResult(job);
                console.log("Final result:", data);
                setResult(data.result);
            }
            else if (statusRes.status === "FAILURE") {
                clearInterval(interval);
                alert("Task failed: " + statusRes.detail);
            }
        }, 2000);
    };

    return (
        <div style={{ padding: "20px" }}>
            <h2>Repo Analyzer</h2>

            <input
                type="text"
                placeholder="Enter GitHub Repo URL"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                style={{ width: "60%", marginRight: "10px" }}
            />

            <button onClick={handleAnalyze}>
                Analyze Repo
            </button>

            {status && <p>Status: {status}</p>}

            {result && (
                <pre style={{ background: "#eee", padding: "10px" }}>
                    {JSON.stringify(result, null, 2)}
                </pre>
            )}
        </div>
    );
}
