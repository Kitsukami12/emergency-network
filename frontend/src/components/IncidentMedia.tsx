import { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_BASE ?? '/api';

type Media = { frame: string | null; clip: string | null };

export default function IncidentMedia({ accidentId }: { accidentId: string }) {
  const [media, setMedia] = useState<Media | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let live = true;
    setMedia(null);
    setFailed(false);
    fetch(`${API}/accidents/${accidentId}/media`)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((m) => live && setMedia(m))
      .catch(() => live && setFailed(true));
    return () => {
      live = false;
    };
  }, [accidentId]);

  const box = { border: '1px solid #30363d', borderRadius: 8, background: '#0d1117', overflow: 'hidden' };
  const note = { padding: 16, color: '#8b949e', fontSize: 13 };

  return (
    <div style={box}>
      <div style={{ padding: '8px 12px', color: '#e6edf3', fontSize: 13, fontWeight: 600 }}>
        Camera recording
      </div>
      {failed && <div style={note}>Could not load the recording.</div>}
      {!failed && !media && <div style={note}>Loading…</div>}
      {media?.clip && (
        <video
          key={media.clip}
          src={`${API}/${media.clip}`}
          poster={media.frame ? `${API}/${media.frame}` : undefined}
          controls autoPlay muted loop playsInline
          style={{ width: '100%', display: 'block', background: '#000' }}
        />
      )}
      {media && !media.clip && media.frame && (
        <img src={`${API}/${media.frame}`} alt="Detection frame" style={{ width: '100%', display: 'block' }} />
      )}
      {media && !media.clip && !media.frame && <div style={note}>No recording for this incident.</div>}
      <div style={{ padding: '6px 12px', color: '#8b949e', fontSize: 11 }}>
        Automated detection from a prototype. Verify before acting.
      </div>
    </div>
  );
}
