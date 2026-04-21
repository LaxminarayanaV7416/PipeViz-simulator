import { useState } from 'react'
import ZipUpload from './components/ZipUpload'
import './App.css'

function App() {
  const [zipFile, setZipFile] = useState(null)

  return (
    <section id="center">
      <h1>PipeViz</h1>
      <ZipUpload onFileSelect={(file) => setZipFile(file)} />
      {zipFile && <p>Ready to simulate: {zipFile.name}</p>}
    </section>
  )
}

export default App