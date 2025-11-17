export default function ResultView({ result }) {
  return (
    <div
      style={{
        background: "#f4f4f4",
        padding: "15px",
        borderRadius: "6px",
        marginTop: "20px",
        maxWidth: "700px",
        overflowX: "auto",
      }}
    >
      <h3>📊 Final Analysis Result</h3>

      <pre>{JSON.stringify(result, null, 2)}</pre>

      {result.report_generated && (
        <p style={{ marginTop: "10px", color: "green" }}>
          ✔ Report Generated Successfully!
        </p>
      )}

      {result.error && (
        <p style={{ marginTop: "10px", color: "red" }}>
          ❌ Error: {result.error}
        </p>
      )}
    </div>
  );
}
