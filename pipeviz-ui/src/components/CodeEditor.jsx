import { useState, useRef } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { cpp } from '@codemirror/lang-cpp'
import { rust } from '@codemirror/lang-rust'

const LANGUAGES = [
    { label: 'C', value: 'c'},
    { label: 'C++', value: 'cpp'},
    { label: 'Rust', value: 'rust'},
]

const LANGUAGE_EXTENSIONS = {
    c:    cpp(),
    cpp:  cpp(),
    rust: rust(),
}
/*
const PLACEHOLDERS = {
    c: '#include <stdio.h>\n\nint main(){\n return 0;\n}',
    cpp: '#include <iostream>\n\nint main(){\n return 0;\n}',
    rust: 'fn main() {\n\n}',
}*/
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

            <div style={{ flex: 1, overflow: 'auto', fontSize: '15px' }}>
                <CodeMirror
                    value={code}
                    onChange={(value) => setCode(value)}
                    extensions={[LANGUAGE_EXTENSIONS[language]]}
                    theme="dark"
                    height="100%"
                    style={{ height: '100%' }}
                />
            </div>

            <button onClick={handleSubmit} style={{ width: 'fit-content' }}>
                Run Simulation
            </button>
        </div>
    )
} 