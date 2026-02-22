import { useEffect, useState } from 'react'

export function SettingsPage() {
  const [token, setToken] = useState('')
  const [cacheDir, setCacheDir] = useState('')
  const [reserveGb, setReserveGb] = useState(10)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/settings')
      .then((r) => r.json())
      .then((s) => {
        setCacheDir(s.model_cache_dir)
        setReserveGb(s.reserve_gb)
      })
  }, [])

  async function saveSettings() {
    const res = await fetch('http://127.0.0.1:8000/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_cache_dir: cacheDir, reserve_gb: reserveGb }),
    })
    if (res.ok) setMessage('Settings saved')
  }

  async function saveToken() {
    const res = await fetch('http://127.0.0.1:8000/settings/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })
    const data = await res.json()
    setMessage(`Token stored using ${data.storage}`)
  }

  return (
    <section>
      <h2>Settings</h2>
      <label>Hugging Face Token</label>
      <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="hf_..." />
      <button onClick={saveToken}>Save Token</button>

      <label>Model cache directory</label>
      <input value={cacheDir} onChange={(e) => setCacheDir(e.target.value)} />

      <label>Memory reserve (GB)</label>
      <input type="number" value={reserveGb} onChange={(e) => setReserveGb(Number(e.target.value))} />
      <button onClick={saveSettings}>Save Settings</button>
      <p>{message}</p>
    </section>
  )
}
