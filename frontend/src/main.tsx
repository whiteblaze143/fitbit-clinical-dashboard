import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import Overview from './pages/Overview'
import Participants from './pages/Participants'
import Compliance from './pages/Compliance'
import Waveforms from './pages/Waveforms'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/participants" element={<Participants />} />
        <Route path="/compliance" element={<Compliance />} />
        <Route path="/waveforms" element={<Waveforms />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
