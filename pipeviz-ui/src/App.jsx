import { useState } from 'react'
import { Group, Panel, Separator } from 'react-resizable-panels'
import FileUpload from './components/FileUpload'
import CodeEditor from './components/CodeEditor'
import PipelineGrid from './components/PipelineGrid'
import './App.css'


const FIBONACCI_C = `#include <stdio.h>
  /* Compute the n-th Fibonacci number recursively. */
  unsigned long fibonacci(unsigned int n) {
      if (n == 0) {
          return 0;
      } else if (n == 1) {
          return 1;
      }
      return fibonacci(n - 1) + fibonacci(n - 2);
  }

  /* main function where program execution starts */
  int main() {
      unsigned int count = 10;

      printf("Fibonacci sequence (first %u terms):\\n", count);

      for (unsigned int i = 0; i < count; i++) {
          unsigned long value = fibonacci(i);
          printf("F(%u) = %lu\\n", i, value);
      }

      return 0;
  }`

const MOCK_DATA = {
    totalCycles: 48,
    instructions: [
      { label: '8ab4: sub sp, sp, #0x40',                          ifCycle: 1  },
      { label: '8ab8: stp x29, x30, [sp, #48]',                    ifCycle: 2  },
      { label: '8abc: add x29, sp, #0x30',                         ifCycle: 3  },
      { label: '8ac0: stur w0, [x29, #-20]',                       ifCycle: 6  },
      { label: '8ac4: stur w0, [x29, #-4]',                        ifCycle: 7  },
      { label: '8ac8: cbz w0, 8ae0',                               ifCycle: 8  },
      { label: '8acc: b 8ad0',                                     ifCycle: 10 },
      { label: '8ad0: ldur w8, [x29, #-20]',                       ifCycle: 12 },
      { label: '8ad4: subs w8, w8, #0x1',                          ifCycle: 15 },
      { label: '8ad8: b.eq 8b00',                                  ifCycle: 16 },
      { label: '8adc: b 8ae8',                                     ifCycle: 18 },
      { label: '8ae0: stur xzr, [x29, #-16]',                      ifCycle: 20 },
      { label: '8ae4: b 8b80',                                     ifCycle: 21 },
      { label: '8ae8: ldur w8, [x29, #-20]',                       ifCycle: 23 },
      { label: '8aec: subs w9, w8, #0x1',                          ifCycle: 26 },
      { label: '8af0: str w9, [sp, #24]',                          ifCycle: 29 },
      { label: '8af4: subs w8, w8, #0x1',                          ifCycle: 30 },
      { label: '8af8: b.cc 8b30',                                  ifCycle: 31 },
      { label: '8afc: b 8b0c',                                     ifCycle: 33 },
      { label: '8b00: mov w8, #0x1',                               ifCycle: 35 },
      { label: '8b04: stur x8, [x29, #-16]',                       ifCycle: 38 },
      { label: '8b08: b 8b80',                                     ifCycle: 39 },
      { label: '8b0c: ldr w0, [sp, #24]',                          ifCycle: 41 },
      { label: '8b10: bl 8ab4',                                    ifCycle: 42 },
      { label: '8b14: ldur w8, [x29, #-20]',                       ifCycle: 44 },
    ]
  }

function App() {
  //const [sourceFile, setSourceFile] = useState(null)
  //const [mode, setMode] = useState('upload')

  function handleCodeSubmit({ code, language }) {
    console.log('User submitted code:', { language, code })
    //later: send to backend API
  }

  return (
    <Group direction="horizontal" style={{ height: '100vh' }}>

      {/* Left panel - code editor */}
      <Panel defaultSize={50} minSize={20} style={{ display: 'flex', flexDirection: 'column', padding: '24px', overflow: 'hidden'}}>
        <h2 style={{ marginTop: 0 }}>Code</h2>
        <CodeEditor
          defaultCode={FIBONACCI_C}
          defaultLanguage="c"
          onCodeSubmuit={handleCodeSubmit}
          />
      </Panel>

      {/* Drag Handle */}
      <Separator style={{
        width: '6px',
        backgroundColor: '#333',
        cursor: 'col-resize',
      }} />

      {/* Right panel - pipeline grid */}
      <Panel defaultSize={50} minSize={20} style={{ display: 'flex', flexDirection: 'column', padding: '24px', overflow: 'auto'}}>
        <h2 style={{ martinTop: 0 }}>Pipeline</h2>
        <PipelineGrid data={MOCK_DATA} />
      </Panel>
    </Group>
  )
}

export default App