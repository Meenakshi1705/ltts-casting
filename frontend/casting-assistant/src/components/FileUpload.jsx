import { useState } from "react";
import { runCastingCheck } from "../api/castingApi";

const FileUpload = ({ onResult }) => {
  const [drawingFile, setDrawingFile] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Casting specifications
  const [castingSpecs, setCastingSpecs] = useState({
    casting_type: "Sand Casting",
    material: "Gray Cast Iron",
    volume: 100,
    process: "Sand Casting",
    tolerance: "Standard",
    surface_finish: "As-cast"
  });

  const castingTypes = [
    "Sand Casting", "Shell Molding", "Investment Casting", "Lost Foam Casting",
    "Gravity Die Casting", "Low Pressure Die Casting", 
    "High Pressure Die Casting (Hot Chamber)", "High Pressure Die Casting (Cold Chamber)",
    "Centrifugal Casting", "Squeeze Casting"
  ];

  const materials = [
    "Gray Cast Iron", "Aluminum A356", "Bronze", "Steel"
  ];

  const processes = [
    "Sand Casting", "Investment Casting", "Die Casting", "Permanent Mold Casting"
  ];

  const handleSubmit = async () => {
    if (!drawingFile) return alert("Please upload a drawing file (PDF/PNG/JPG)");

    setLoading(true);
    try {
      const result = await runCastingCheck(drawingFile, castingSpecs);
      onResult(result);
    } catch (err) {
      console.error(err);
      alert("Error running casting check: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSpecChange = (field, value) => {
    setCastingSpecs(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="card">
      <h2>Casting Design Analysis</h2>
      
      <div className="file-section">
        <h3>Upload Drawing</h3>
        <div className="file-input-group">
          <label>
            Drawing File (PDF, PNG, or JPG):
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => setDrawingFile(e.target.files[0])}
            />
            {drawingFile && (
              <span className="file-info">
                Selected: {drawingFile.name} ({(drawingFile.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            )}
          </label>
        </div>
        <p className="info-text">
          <strong>Note:</strong> The system uses a constant set of 22 casting design rules. 
          Simply upload your drawing and specify the casting parameters below.
        </p>
      </div>

      <div className="specs-section">
        <h3>Casting Specifications</h3>
        
        <div className="specs-grid">
          <label>
            Casting Type:
            <select 
              value={castingSpecs.casting_type}
              onChange={(e) => handleSpecChange('casting_type', e.target.value)}
            >
              {castingTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </label>

          <label>
            Material:
            <select 
              value={castingSpecs.material}
              onChange={(e) => handleSpecChange('material', e.target.value)}
            >
              {materials.map(material => (
                <option key={material} value={material}>{material}</option>
              ))}
            </select>
          </label>

          <label>
            Production Volume:
            <input
              type="number"
              min="1"
              value={castingSpecs.volume}
              onChange={(e) => handleSpecChange('volume', parseInt(e.target.value) || 100)}
            />
          </label>

          <label>
            Casting Process:
            <select 
              value={castingSpecs.process}
              onChange={(e) => handleSpecChange('process', e.target.value)}
            >
              {processes.map(process => (
                <option key={process} value={process}>{process}</option>
              ))}
            </select>
          </label>

          <label>
            Tolerance:
            <input
              type="text"
              value={castingSpecs.tolerance}
              onChange={(e) => handleSpecChange('tolerance', e.target.value)}
              placeholder="e.g., ±0.5mm"
            />
          </label>

          <label>
            Surface Finish:
            <input
              type="text"
              value={castingSpecs.surface_finish}
              onChange={(e) => handleSpecChange('surface_finish', e.target.value)}
              placeholder="e.g., Ra 3.2"
            />
          </label>
        </div>
      </div>

      <button 
        onClick={handleSubmit} 
        disabled={loading || !drawingFile}
        className="analyze-button"
      >
        {loading ? "Analyzing..." : "Run Analysis"}
      </button>
    </div>
  );
};

export default FileUpload;
