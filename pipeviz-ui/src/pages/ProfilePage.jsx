import { useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'

const AUTHORS = [
    {
        id: 'laxminarayana',
        name: 'Laxminarayana Vadnala',
        role: 'Project Lead, Backend Developer',
        lab: 'The Cooperative Computing Lab',
        bio: 'ADD BIO HERE.',
        email: 'lvadnala@nd.edu',
    },
    {
        id: 'patrick',
        name: 'Patrick Do',
        role: 'LLM Agent Developer',
        lab: 'Machine Learning Lab',
        bio: 'ADD BIO HERE.',
        email: 'mdo23@nd.edu',
    },
    {
        id: 'jude',
        name: 'Jude Lynch',
        role: 'Frontend Developer',
        lab: "Master's Student",
        bio: 'ADDIO BIO HERE',
        email: 'jlynch23@nd.edu'
    },
]

export default function ProfilesPage() {
    const { hash } = useLocation()
    
    useEffect(() => {
        if (hash) {
            const el = document.getElementById(hash.slice(1))
            if (el) el.scrollIntoView({ behavior: 'smooth' })
        }
    }, [hash])
    return(
        <div style={{ maxWidth: '720px', margin: '0 auto', padding: '40px'}}>
            <Link to="/" style={{ fontSize: '14px', color: '#9c3af'}}>
                Return to PipeViz
            </Link>
            {AUTHORS.map((author) => (
                <section
                    key={author.id}
                    id={author.id}
                    style={{
                        minHeight: '100vh',
                        paddingTop: '80px',
                        borderBottom: '1px solid #333',
                    }}
                >
                    <h1 style={{ fontSize: '36px', margineBottom: '8px'}}>{author.name}</h1>
                    <p style={{ color: '#9ca3af', fontSize: '16px', marginBottom: '24px'}}>{author.role}</p>
                    <p style={{ lineHeight: '1.7' }}>{author.bio}</p>
                    {author.email && (
                        <p style={{ marginTop: '16px', fontSize: '14px', color: '#9ca3af'}}>
                            {author.emailx}
                        </p>
                    )}
                </section>
            ))}
        </div>
    )
}