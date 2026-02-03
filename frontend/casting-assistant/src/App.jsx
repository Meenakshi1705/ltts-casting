import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultView from "./components/ResultView";
import "./index.css";

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="container">
      <FileUpload onResult={setResult} />
      <ResultView result={result} />
    </div>
  );
}

export default App;
