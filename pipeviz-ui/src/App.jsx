import { useState } from 'react'
import ZipUpload from './components/ZipUpload'

import PipelineGrid from './components/PipelineGrid'
import './App.css'

const MOCK_DATA = {
  totalCycles: 12,
  instructions: [
    { label: '8ab4: sub sp, sp, #0x40',      ifCycle: 1},
    { label: '8ab8: stp x29, x30,[sp, #48]', ifCycle: 2},

    { label: '8abc: add x29, sp, #0x30', ifCycle: 3},
    { label: '8ab0: stur w0, [x29, #-20]', ifCycle: 6},

    { label: '8ac4: stur w0, [x29, #-4]', ifCycle: 7},
  ]
}

function App() {
  const [zipFile, setZipFile] = useState(null)

  return (
    <div style={{ padding: '32px' }}>
      <h1>PipeViz</h1>
      <ZipUpload onFileSelect={(file) => setZipFile(file)} />
      {zipFile && <p>Ready to simulate: {zipFile.name}</p>}

      <PipelineGrid data={MOCK_DATA} />
    </div>
  )
}

export default App