const BASE_URL = "http://127.0.0.1:8000/api";

export async function analyzeRepo(repoUrl) {
    try {
        const res = await fetch(`${BASE_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ repo_url: repoUrl }),
        });
        return res.json();
    } catch (err) {
        console.error("Analyze API error:", err);
        throw err;
    }
}

export async function checkStatus(jobId) {
    const res = await fetch(`${BASE_URL}/status/${jobId}`);
    return res.json();
}

export async function getResult(jobId) {
    const res = await fetch(`${BASE_URL}/result/${jobId}`);
    return res.json();
}
