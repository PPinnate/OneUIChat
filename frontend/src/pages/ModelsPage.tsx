import { useEffect, useMemo, useState } from 'react'

type Fit = { status: string; alternatives: string[]; breakdown: { estimated_total_gb: number; budget_gb: number } }
type Variant = { id: string; fit: Fit }
type Model = { id: string; display_name: string; license: string; variants: Variant[] }

type ExploreResult = {
  probe: { available: boolean; auth_required: boolean; total_gb: number; error: string | null }
  fit: Fit
  disk: { free_gb: number; enough_for_download: boolean }
  ready_to_download: boolean
  ready_to_load: boolean
}

export function ModelsPage() {
  const [models, setModels] = useState<Model[]>([])
  const [selected, setSelected] = useState<Record<string, string>>({})
  const [message, setMessage] = useState('')
  const [eventLines, setEventLines] = useState<string[]>([])
  const [inspect, setInspect] = useState<Record<string, ExploreResult>>({})

  useEffect(() => {
    fetch('http://127.0.0.1:8000/models')
      .then((r) => r.json())
      .then((payload) => {
        setModels(payload.models)
        const init: Record<string, string> = {}
        payload.models.forEach((m: Model) => {
          init[m.id] = m.variants[0]?.id
        })
        setSelected(init)
      })
      .catch((e) => setMessage(String(e)))

    const ws = new WebSocket('ws://127.0.0.1:8000/ws/events')
    ws.onmessage = (evt) => {
      const parsed = JSON.parse(evt.data)
      if (parsed.type === 'download_progress') {
        setEventLines((prev) => [`${parsed.status}: ${parsed.file}`, ...prev].slice(0, 8))
      }
      if (parsed.type === 'download_complete') {
        setEventLines((prev) => [`complete: ${parsed.repo_id} ${parsed.total_gb}GB`, ...prev].slice(0, 8))
      }
    }
    return () => ws.close()
  }, [])

  const sortedModels = useMemo(() => models, [models])

  async function explore(modelId: string) {
    const variantId = selected[modelId]
    const res = await fetch('http://127.0.0.1:8000/models/explore', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, variant_id: variantId }),
    })
    const data: ExploreResult = await res.json()
    setInspect((prev) => ({ ...prev, [`${modelId}:${variantId}`]: data }))
    if (data.probe.auth_required) {
      setMessage('HF token required for this model repo. Add it in Settings.')
    } else if (!data.disk.enough_for_download) {
      setMessage(`Not enough disk space. Free: ${data.disk.free_gb} GB`)
    } else {
      setMessage('Model exploration complete. Ready status updated.')
    }
  }

  async function download(modelId: string) {
    const variantId = selected[modelId]
    setMessage(`Downloading ${modelId}:${variantId} ...`)
    const res = await fetch('http://127.0.0.1:8000/models/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, variant_id: variantId }),
    })
    const data = await res.json()
    setMessage(`Downloaded ${data.repo_id} (${(data.total_bytes / (1024 ** 3)).toFixed(2)} GB)`)
  }

  return (
    <section>
      <h2>Models</h2>
      <p>{message}</p>
      <div className="card">
        <strong>Live download log</strong>
        {eventLines.length === 0 ? <div className="muted">No events yet.</div> : eventLines.map((line) => <div key={line}>{line}</div>)}
      </div>
      {sortedModels.map((m) => {
        const variantId = selected[m.id]
        const key = `${m.id}:${variantId}`
        const inspected = inspect[key]
        return (
          <div key={m.id} className="card">
            <strong>{m.display_name}</strong>
            <div className="license">License: {m.license}</div>
            <select value={variantId} onChange={(e) => setSelected({ ...selected, [m.id]: e.target.value })}>
              {m.variants.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.id} ({v.fit.status})
                </option>
              ))}
            </select>
            {inspected && (
              <div className="hint">
                <div>HF available: {String(inspected.probe.available)} | Auth required: {String(inspected.probe.auth_required)}</div>
                <div>Total size: {inspected.probe.total_gb} GB | Disk free: {inspected.disk.free_gb} GB</div>
                <div>Load fit: {inspected.fit.status} (est {inspected.fit.breakdown.estimated_total_gb} / budget {inspected.fit.breakdown.budget_gb} GB)</div>
                {inspected.fit.status === 'DOES_NOT_FIT' && inspected.fit.alternatives.length > 0 && (
                  <div>Try installed alternatives that fit: {inspected.fit.alternatives.join(', ')}</div>
                )}
              </div>
            )}
            <div className="row">
              <button onClick={() => explore(m.id)}>Explore availability + size</button>
              <button onClick={() => download(m.id)}>Download selected variant</button>
              <button disabled>Load (MVP-1)</button>
            </div>
          </div>
        )
      })}
    </section>
  )
}
