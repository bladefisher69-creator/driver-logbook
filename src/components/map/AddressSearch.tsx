import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../../api/client';

interface Suggestion {
  id: string;
  place_name: string;
  address?: string;
  lat?: number;
  lng?: number;
}

interface Props {
  onSelect: (s: Suggestion) => void;
  placeholder?: string;
}

export default function AddressSearch({ onSelect, placeholder = 'Search address...' }: Props) {
  const [q, setQ] = useState('');
  const [results, setResults] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  useEffect(() => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    if (!q) return setResults([]);
    timeoutRef.current = window.setTimeout(async () => {
      setLoading(true);
      try {
        const res = await apiClient.get<Suggestion[]>(`/search/address/?q=${encodeURIComponent(q)}`, { requiresAuth: false });
        setResults(res);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => { if (timeoutRef.current) window.clearTimeout(timeoutRef.current); };
  }, [q]);

  return (
    <div className="relative">
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 border rounded"
      />
      {q && (
        <div className="absolute left-0 right-0 bg-white border rounded mt-1 max-h-64 overflow-auto z-50">
          {loading && <div className="p-2">Searching...</div>}
          {!loading && results.length === 0 && <div className="p-2 text-sm text-slate-500">No results</div>}
          {results.map(r => (
            <div key={r.id} className="p-2 hover:bg-slate-100 cursor-pointer" onClick={() => { onSelect(r); setQ(''); setResults([]); }}>
              <div className="text-sm font-medium">{r.place_name}</div>
              {r.address && <div className="text-xs text-slate-500">{r.address}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
