import { useState, useEffect } from "react";

const ResultView = ({ result }) => {
  const [latestReport, setLatestReport] = useState(null);

  // Fetch the latest report when component mounts or result changes
  useEffect(() => {
    const fetchLatestReport = async () => {
      try {
        const response = await fetch('http://localhost:8000/latest-report');
        const data = await response.json();
        if (data.filename) {
          setLatestReport(data);
        }
      } catch (error) {
        console.error('Error fetching latest report:', error);
      }
    };

    fetchLatestReport();
  }, [result]);

  if (!result) return null;

  const { status, summary, casting_context, excel_filename, pdf_filename } = result;

  if (status !== "success") {
    return (
      <div className="card error">
        <h3>Analysis Failed</h3>
        <p>Error: {result.error || "Unknown error occurred"}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>Analysis Complete</h3>
      
      <div className="result-summary">
        <div className="files-info">
          <h4>Input Files</h4>
          <p><strong>Rules:</strong> {excel_filename}</p>
          <p><strong>Drawing:</strong> {pdf_filename}</p>
        </div>

        <div className="casting-info">
          <h4>Casting Specifications</h4>
          <div className="specs-display">
            <span><strong>Type:</strong> {casting_context.casting_type}</span>
            <span><strong>Material:</strong> {casting_context.material}</span>
            <span><strong>Volume:</strong> {casting_context.volume.toLocaleString()} parts</span>
            <span><strong>Process:</strong> {casting_context.process}</span>
            <span><strong>Tolerance:</strong> {casting_context.tolerance}</span>
            <span><strong>Surface Finish:</strong> {casting_context.surface_finish}</span>
          </div>
        </div>

        {summary && (
          <div className="analysis-summary">
            <h4>Results Summary</h4>
            <div className="summary-stats">
              <div className="stat compliant">
                <span className="count">{summary.results?.compliant || 0}</span>
                <span className="label">Compliant</span>
              </div>
              <div className="stat non-compliant">
                <span className="count">{summary.results?.non_compliant || 0}</span>
                <span className="label">Non-compliant</span>
              </div>
              <div className="stat needs-review">
                <span className="count">{summary.results?.needs_review || 0}</span>
                <span className="label">Needs Review</span>
              </div>
            </div>
            
            <p><strong>Total Checks:</strong> {summary.total_checks || 0}</p>
            <p><strong>Successful Evaluations:</strong> {summary.successful_evaluations || 0}</p>
          </div>
        )}

        {/* Download section moved right after Results Summary */}
        {latestReport && (
          <div className="download-section">
            <h4>Detailed Report</h4>
            <a 
              href={`http://localhost:8000${latestReport.path}`}
              download
              className="download-button"
            >
              Download Latest Excel Report ({latestReport.filename})
            </a>
            <p style={{fontSize: '12px', color: '#666', marginTop: '10px'}}>
              Note: If analysis shows 0 results above, the Excel file still contains the actual analysis data.
            </p>
          </div>
        )}

        {summary?.details && summary.details.length > 0 && (
          <div className="preview-section">
            <h4>Preview</h4>
            <div className="preview-table">
              <table>
                <thead>
                  <tr>
                    <th>Rule</th>
                    <th>Check Item</th>
                    <th>Result</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.details.map((item, index) => (
                    <tr key={index}>
                      <td>{item["Rule ID"]}</td>
                      <td>{item["Checklist Item"]?.substring(0, 50)}...</td>
                      <td className={`result ${item["Result (Yes/No)"]?.toLowerCase().replace(' ', '-')}`}>
                        {item["Result (Yes/No)"]}
                      </td>
                      <td>{item["Notes / Observations"]?.substring(0, 100)}...</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultView;
