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
        photo: '/lax.jpg',
        github: 'https://github.com/LaxminarayanaV7416',
        linkedin: 'https://www.linkedin.com/in/laxminarayana-vadnala/',
        personalsite: 'https://laxminarayanav7416.github.io/'
    },
    {
        id: 'patrick',
        name: 'Patrick Do',
        role: 'LLM Agent Developer',
        lab: 'Machine Learning Lab',
        bio: 'ADD BIO HERE.',
        email: 'mdo23@nd.edu',
        photo: '/patrick.jpeg',
        github: 'https://github.com/patdmp',
        linkedin: 'https://www.linkedin.com/in/patrick-d/'
    },
    {
        id: 'jude',
        name: 'Jude Lynch',
        role: 'Frontend Developer',
        lab: "Master's Student",
        bio: 'Classics major who found himself here',
        email: 'jlynch23@nd.edu',
        photo: '/jude.jpg',
        github: 'https://github.com/GiudaJude',
        linkedin: 'https://www.linkedin.com/in/jude-lynch/',
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
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh'}}>
            {/* Header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "10px 24px",
                borderBottom: "1px solid #333",
                flexShrink: 0,
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 10,
                backgroundColor: '#16171d',
            }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', color: 'inherit'}}>
                <img
                  src="/ND_Monogram_10127_RGB.png"
                  alt="Logo"
                  style={{ height: "40px" }}
                />
                <h1 style={{ margin: 0, fontSize: "22px" }}>PipeViz</h1>
            </Link>
            <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
                {/* Team names */}
                <div style={{ display: "flex", gap: "24px", fontSize: "14px"}}>
                    <Link to="/profiles#laxminarayana" style={{ color: '#ae9142' }}>Laxminarayana Vadnala</Link>
                    <Link to="/profiles#patrick" style={{ color: '#ae9142' }}>Patrick Do</Link>
                    <Link to="/profiles#jude" style={{ color: '#ae9142' }}>Jude Lynch</Link>
                </div>
            </div>
        </div>
              

        <div style={{ maxWidth: '720px', margin: '0 auto', padding: '40px'}}>
            {AUTHORS.map((author) => (
                <section
                    key={author.id}
                    id={author.id}
                    style={{
                        minHeight: '100vh',
                        paddingTop: '80px',
                        borderBottom: '1px solid #333',
                }}>
                    <h1 style={{ fontSize: '36px', marginBottom: '8px', marginTop: 0}}>{author.name}</h1>
                    <p style={{ color: '#9ca3af', fontSize: '16px', marginBottom: '24px'}}>{author.role}</p>
                    
                    <img
                        src={author.photo}
                        alt={author.name}
                        style={{ width: '320px', height: '320px',  objectFit: 'cover', marginBottom: '24px'}}
                    />
                    <p style={{ lineHeight: '1.7', maxWidth: '600px', margin: '0 auto 16px auto'}}>{author.bio}</p>
                    {author.email && (
                        <p style={{ marginTop: '16px', fontSize: '14px', color: '#9ca3af', marginBottom: '20px'}}>
                            {author.email}
                        </p>
                    )}
                    <div style={{display: 'flex', gap: '12px', marginTop: '20px'}}>
                        {author.github && (<a href={author.github ?? '#'} 
                        target="_blank" 
                        rel="noreferrer" 
                        style={{ color: '#9ca3af',
                                    fontSize: '13px',
                                    textDecoration: 'none',
                                    borderRadius: '6px',
                                    padding: '6px 12px'
                        }}>
                            <img
                                src="/GitHub_Invertocat_White.svg"
                                alt="GitHub"
                                style={{ width: '32px', height:'32px'}}
                            />
                        </a>)}
                        {author.linkedin && (<a href={author.linkedin ?? '#'} 
                        target="_blank" 
                        rel="noreferrer" 
                        style={{ color: '#9ca3af',
                                    fontSize: '13px',
                                    textDecoration: 'none',
                                    borderRadius: '6px',
                                    padding: '6px 12px'
                        }}>
                            <img
                                src="/InBug-White.png"
                                alt="LinkedIn"
                                style={{ width: '32px', height:'32px'}}
                            />
                        </a>)}
                        {author.personalsite && (<a href={author.personalsite ?? '#'} 
                        target="_blank" 
                        rel="noreferrer" 
                        style={{ color: '#ffffff',
                                    fontSize: '13px',
                                    textDecoration: 'none',
                                    border: '2px solid #ffffff',
                                    borderRadius: '10px',
                                    padding: '10x 20px',
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    height: '32px',
                                    boxSizing: 'border-box'
                        }}>
                            Website
                        </a>)}
                    </div>
                </section>
            ))}
        </div>
    </div>
    )
}