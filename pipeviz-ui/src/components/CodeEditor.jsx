import { useState } from 'react'

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

export default function CodeEditor({ onCodeSubmuit }) {
    const [language, setLanguage] = useState('c')
    const [code, setCode] = useState('')

    function handleSubmit() {
        if (!code.trim()) {
            alert('Please write some code first')
            return
        }
        onCodeSubmuit({ code, language })
    }


return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{ width: 'fit-content', padding: '6px 10px', fontSize: '14px' }}
        >
            {LANGUAGES.map(lang => (
                <option key={lang.value} value={lang.value}>{lang.label}</option>
            ))}
        </select>

        <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={PLACEHOLDERS[language]}
            spellCheck={false}
            style={{
                fontFamily: 'monospace',
                fontSize: '13px',
                width: '600px',
                height: '300px',
                padding: '12px',
                backgroundColor: '#1a1a1a',
                color: '#fff',
                border: '1px solid #333',
                borderRadius: '6px',
                resize: 'vertical'
            }}
        />

        <button onClick={handleSubmit} style={{ width: 'fit-content' }}>
            Run Simulation
        </button>
    </div>
    )
} 