import { FormEvent, useState } from 'react'

type Message = { role: 'user' | 'assistant'; content: string }

export function ChatPage() {
  const [systemPrompt, setSystemPrompt] = useState('You are QwenWorkbench local assistant.')
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Welcome! Ask anything. I will keep everything local-first.' },
  ])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!draft.trim()) return
    const userMessage = { role: 'user' as const, content: draft }
    setMessages((prev) => [...prev, userMessage])
    setDraft('')

    const res = await fetch('http://127.0.0.1:8000/tasks/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: userMessage.content, system_prompt: systemPrompt }),
    })
    const data = await res.json()
    setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
  }

  return (
    <section className="chat-layout">
      <aside className="chat-sidebar">
        <h3>Sessions</h3>
        <button className="full">+ New Chat</button>
        <p className="muted">Model: Chat (worker integration in MVP-2)</p>
      </aside>

      <div className="chat-main">
        <div className="system-row">
          <label>System prompt</label>
          <textarea value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)} rows={2} />
        </div>

        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={`${msg.role}-${idx}`} className={`bubble ${msg.role}`}>
              {msg.content}
            </div>
          ))}
        </div>

        <form className="composer" onSubmit={onSubmit}>
          <input
            placeholder="Message QwenWorkbench..."
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </section>
  )
}
