const STAGE_COLORS = {
    IF:  '#083D77', // Regal Navy
    IS:  '#995D81', // Dusty Lavendar
    EXE: '#DA4167', // Magneta Bloom
    MEM: '#F4D35E', // Royal Gold
    WB:  '#F78764' // Coral Glow
}

function getStage(ifCycle, cycle){
    if (cycle === ifCycle)     return 'IF'
    if (cycle === ifCycle + 1) return 'IS'
    if (cycle === ifCycle + 2) return 'EXE'
    if (cycle === ifCycle + 3) return 'MEM'
    if (cycle === ifCycle + 4) return 'WB'

    return ''
}

export default function PipelineGrid({ data }) {
    const { totalCycles, instructions } = data

    const cycles = Array.from({ length: totalCycles }, (_, i ) => i + 1)

    return (
        <div style={{ overflowX: 'auto', width: '100%', maxHeight: '80vh' }}>
            <table style={{ borderCollapse: 'seperate', borderSpacing: 0, whiteSpace: 'nowrap' }}>
                <thead>
                    <tr>
                        <th style={headerCell}>Instruction</th>
                        {cycles.map(c => (
                            <th key={c} style={headerCell}>C{c}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {instructions.map((instr) => (
                        <tr key={instr.label}>
                            <td style={labelCell}>{instr.label}</td>
                            {cycles.map(c => {
                                const stage = getStage(instr.ifCycle, c)

                                return (
                                    <td key={c} style={stageCell(stage)}>
                                        {stage}
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

function stageCell(stage) {
    return {
        pardding: '6px 10px',

        border: '1px solid #333',
        textAlign: 'center',
        fontWeight: stage? 'bold' : 'normal',
        fontSize: '12px',

        backgroundColor: stage ? STAGE_COLORS[stage] : 'transparent',
        color: stage? '#fff' : 'transparent',

        minWidth: '40px',
    }
}