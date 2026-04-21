import { useRef, useState } from 'react'

export default function ZipUpload({ onFileSelect }){
    const [selectedFile, setSelectedFile] = useState(null)
    const inputRef = useRef(null)
    const VALID_EXTENSIONS = ['.rs', '.c', '.cpp']

    function handleFileChange(event) {
        const file = event.target.files[0]

        if (!file) return

        const hasValidExtension = VALID_EXTENSIONS.some(ext => file.name.endsWith(ext))
        if (!hasValidExtension) {
            alert('Please upload a .rs, .c, or .cpp file')
            return
        }

        setSelectedFile(file)
        onFileSelect(file)
    }

    return (
        <div className="file-upload">
            {/* Hidden native file input - only accepts .zip*/}
            <input
                ref={inputRef}
                type="file"
                accept=".rs,.c,.cpp"
                onChange={handleFileChange}
                style={{ display: 'none' }}
            />

            {/* Styled button that clicks the hidden input */}
            <button onClick={() => inputRef.current.click()}>
                Upload Source File  (.rs / .c / .cpp)
            </button>

            {/* Show filename once selected */}
            {selectedFile && (
                <p className="file-name">Selected: {selectedFile.name}</p>
            )}
        </div>
    )
}