import { useRef, useState } from 'react'

export default function ZipUpload({ onFileSelect }){
    const [selectedFile, setSelectedFile] = useState(null)
    const inputRef = useRef(null)

    function handleFileChange(event) {
        const file = event.target.files[0]

        if (!file) return

        if (!file.name.endsWith('.zip')) {
            alert('Please upload a .zip file')
            return
        }

        setSelectedFile(file)
        onFileSelect(file)
    }

    return (
        <div className="zip-upload">
            {/* Hidden native file input - only accepts .zip*/}
            <input
                ref={inputRef}
                type="file"
                accept=".zip"
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />

            {/* Styled button that clicks the hidden input */}
            <button onClick={() => inputRef.current.click()}>
                Upload ZIP
            </button>

            {/* Show filename once selected */}
            {selectedFile && (
                <p className="file-name">Selected: {selectedFile.name}</p>
            )}
        </div>
    )
}