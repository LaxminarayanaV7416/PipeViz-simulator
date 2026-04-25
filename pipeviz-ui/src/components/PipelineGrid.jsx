const STAGE_COLORS = {
    IF:  '#083D77',
    IS:  '#995D81',
    EXE: '#DA4167',
    MEM: '#F4D35E',
    WB:  '#F78764',
}

const STALL_COLORS = {
    IF:  '#041e3c',
    IS:  '#4d2e40',
    EXE: '#6d1f32',
    MEM: '#7a6a2f',
    WB:  '#7c3c2f',
}

function parseCell(cell) {
    if (!cell) return { stage: '', isStall: false }
    const isStall = cell.includes('[STALL]')
    const stage = cell.split('[')[0]
    return { stage, isStall }
}

export default function PipelineGrid({ rows }) {
    if (!rows || rows.length === 0) {
        return (
            <div style={{ color: '#555', fontSize: '14px', marginTop: '16px' }}>
                Run a simulation to see the pipeline diagram.
            </div>
        )
    }

    const cycleKeys = Object.keys(rows[0])
        .filter(k => /^C\d+$/.test(k))
        .sort((a, b) => parseInt(a.slice(1)) - parseInt(b.slice(1)))

    return (
        <div style={{ overflowX: 'auto', width: '100%', maxHeight: '80vh' }}>
            <table style={{ borderCollapse: 'separate', borderSpacing: 0, whiteSpace: 'nowrap' }}>
                <thead>
                    <tr>
                        <th style={headerCell}>Instruction</th>
                        {cycleKeys.map(k => (
                            <th key={k} style={headerCell}>{k}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, i) => (
                        <tr key={i}>
                            <td style={labelCell}>{row.instruction}</td>
                            {cycleKeys.map(k => {
                                const { stage, isStall } = parseCell(row[k])
                                return (
                                    <td key={k} style={stageCell(stage, isStall)}>
                                        {stage || ''}
                                        {isStall && stage
                                            ? <span style={{ fontSize: '9px', opacity: 0.8 }}> S</span>
                                            : null}
                                    </td>
                                )
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

const headerCell = {
    padding: '6px 12px',
    border: '1px solid #333',
    textAlign: 'center',
    fontSize: '13px',
    position: 'sticky',
    top: 0,
    zIndex: 2,
    backgroundColor: '#242424',
}

const labelCell = {
    padding: '6px 12px',
    border: '1px solid #333',
    fontFamily: 'monospace',
    fontSize: '12px',
    minWidth: '260px',
    position: 'sticky',
    left: 0,
    zIndex: 1,
    backgroundColor: '#242424',
}

function stageCell(stage, isStall) {
    const colors = isStall ? STALL_COLORS : STAGE_COLORS
    return {
        padding: '6px 10px',
        border: isStall ? '1px dashed #555' : '1px solid #333',
        textAlign: 'center',
        fontWeight: stage ? 'bold' : 'normal',
        fontSize: '12px',
        backgroundColor: stage ? colors[stage] : 'transparent',
        color: stage ? '#fff' : 'transparent',
        minWidth: '44px',
    }
}
