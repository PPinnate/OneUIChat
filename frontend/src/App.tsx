import { useMemo, useState } from 'react'
import { ChatPage } from './pages/ChatPage'
import { ModelsPage } from './pages/ModelsPage'
import { SettingsPage } from './pages/SettingsPage'

const tabs = ['Chat', 'Code', 'Speech', 'OCR', 'Image', 'Video (Experimental)', 'Models', 'Settings', 'Logs']

export function App() {
  const [active, setActive] = useState('Chat')

  const content = useMemo(() => {
    if (active === 'Chat') return <ChatPage />
    if (active === 'Models') return <ModelsPage />
    if (active === 'Settings') return <SettingsPage />
    return <div className="placeholder">{active} is scaffolded for upcoming MVPs.</div>
  }, [active])

  return (
    <div className="app">
      <header>
        <h1>QwenWorkbench</h1>
      </header>
      <nav>
        {tabs.map((tab) => (
          <button key={tab} className={tab === active ? 'active' : ''} onClick={() => setActive(tab)}>
            {tab}
          </button>
        ))}
      </nav>
      <main>{content}</main>
    </div>
  )
}
