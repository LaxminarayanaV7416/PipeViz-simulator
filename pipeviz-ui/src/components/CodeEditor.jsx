import { useState, useRef } from 'react'

const LANGUAGES = [
    { label: 'C', value: 'c'},
    { label: 'C++', value: 'cpp'},
    { label: 'Rust', value: 'rust'},
]

const PLACEHOLDERS = {
    c: '#include <stdio.h>\n\nint main(){\n return 0;\n}',
    cpp: '#include <iostream>\n\nint main(){\n return 0;\n}',
    rust: 'fn main() {\n\n}',
}
export default function CodeEditor({ onCodeSubmuit, defaultCode = '', defaultLanguage = 'c' }) {
    const [language, setLanguage] = useState(defaultLanguage)
    const [code, setCode] = useState(defaultCode)
    const fileInputRef = useRef(null)

    function handleFileUpload(event) {
        const file = event.target.files[0]
        if (!file) return

        if (file.name.endsWith('.c')) setLanguage('c')
        if (file.name.endsWith('.cpp')) setLanguage('cpp')
        if (file.name.endsWith('.rs')) setLanguage('rust')
        
        const reader = new FileReader()
        reader.onload = (e) => setCode(e.target.result)
        
        reader.readAsText(file)
    }

    function handleSubmit() {
        if (!code.trim()) {
            alert('Please write some code first')
            return
        }
        onCodeSubmuit({ code, language })
    }


    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '12px' }}>
            <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                style={{ width: 'fit-content', padding: '6px 10px', fontSize: '14px' }}
            >
                {LANGUAGES.map(lang => (
                    <option key={lang.value} value={lang.value}>{lang.label}</option>
                ))}
            </select>

            <input
                ref={fileInputRef}
                type="file"
                accept=".c,.cpp,.rs"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
            />
            <button
                onClick={() => fileInputRef.current.click()}
                style={{ width: 'fit-content' }}
            >
                Upload File
            </button>

            <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                spellCheck={false}
                style={{
                    flex: 1,
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    width: '100%',
                    padding: '12px',
                    backgroundColor: '#1a1a1a',
                    color: '#fff',
                    border: '1px solid #333',
                    borderRadius: '6px',
                    resize: 'none',
                    boxSizing: 'border-box',
                }}
            />

            <button onClick={handleSubmit} style={{ width: 'fit-content' }}>
                Run Simulation
            </button>
        </div>
    )
} 