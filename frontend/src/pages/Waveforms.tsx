import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import axios from "axios"
import Plotly from 'plotly.js-dist-min'
import createPlotlyComponent from 'react-plotly.js/factory'

const createPlotlyComponentFactory = (createPlotlyComponent as any).default || createPlotlyComponent
const Plot = createPlotlyComponentFactory(Plotly)

export default function Waveforms() {
  const [indexData, setIndexData] = useState<any[]>([])
  const [selectedPid, setSelectedPid] = useState<string>("")
  const [selectedRecord, setSelectedRecord] = useState<any>(null)

  const [waveform, setWaveform] = useState<any>(null)
  const [windowSec, setWindowSec] = useState(10)
  const [startAt, setStartAt] = useState(0)
  const [unit, setUnit] = useState("mV")
  const [applyFilter, setApplyFilter] = useState(true)

  const [artifact, setArtifact] = useState(false)
  const [label, setLabel] = useState("Unsure")
  const [comment, setComment] = useState("")

  useEffect(() => {
    axios.get("/api/data/index").then(res => {
      setIndexData(res.data)
      const pids = Array.from(new Set(res.data.map((d: any) => d.studyId)))
      if (pids.length > 0) setSelectedPid(pids[0] as string)
    }).catch(console.error)
  }, [])

  const participantRecords = indexData.filter(d => d.studyId === selectedPid)

  useEffect(() => {
    if (participantRecords.length > 0 && !selectedRecord) {
      setSelectedRecord(participantRecords[0])
    }
  }, [selectedPid, participantRecords])

  useEffect(() => {
    if (selectedRecord) {
      fetchWaveform()
      fetchAnnotations()
    }
  }, [selectedRecord, startAt, windowSec, unit, applyFilter])

  const fetchWaveform = async () => {
    try {
      const res = await axios.get(`/api/data/waveform/${selectedRecord.studyId}/${selectedRecord.stableEcgId}`, {
        params: { start_sec: startAt, window_sec: windowSec, unit, apply_filter: applyFilter, fs: selectedRecord.samplingFrequency || 250.0 }
      })
      setWaveform(res.data)
    } catch (e) {
      console.error(e)
      setWaveform(null)
    }
  }

  const fetchAnnotations = async () => {
    if (!selectedRecord) return
    try {
      const artRes = await axios.get(`/api/db/artifacts/${selectedRecord.stableEcgId}`)
      setArtifact(artRes.data.artifact)

      const labRes = await axios.get(`/api/db/labels/${selectedRecord.stableEcgId}`)
      if (labRes.data.label) {
        setLabel(labRes.data.label)
        setComment(labRes.data.comment || "")
      } else {
        setLabel("Unsure")
        setComment("")
      }
    } catch(e) {
      console.error(e)
    }
  }

  const saveArtifact = async (val: boolean) => {
    setArtifact(val)
    try {
      await axios.post("/api/db/artifacts", { stableEcgId: selectedRecord.stableEcgId, artifact: val })
    } catch (e) { console.error(e) }
  }

  const saveMetrics = async () => {
    if (!waveform || !selectedRecord) return
    try {
      await axios.post("/api/db/metrics", {
        stableEcgId: selectedRecord.stableEcgId,
        startTime: selectedRecord.startTime,
        classification: selectedRecord.classification,
        fs: selectedRecord.samplingFrequency || 250.0,
        window_sec: windowSec,
        start_at_sec: startAt,
        unit,
        hr_bpm: waveform.metrics.hr,
        rmssd_ms: waveform.metrics.rmssd,
        sdnn_ms: waveform.metrics.sdnn,
        pnn50_pct: waveform.metrics.pnn50,
        artifact
      })
      alert("Metrics saved successfully")
    } catch (e) {
      alert("Failed to save metrics")
    }
  }

  const saveLabel = async () => {
    if (!selectedRecord) return
    try {
      await axios.post("/api/db/labels", {
        stableEcgId: selectedRecord.stableEcgId,
        startTime: selectedRecord.startTime,
        classification: selectedRecord.classification,
        label,
        comment
      })
      alert("Label saved successfully")
    } catch (e) {
      alert("Failed to save label")
    }
  }

  return (
    <Layout>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-800">ECG Waveform Viewer</h2>
        <p className="text-slate-500 mt-1">Review individual recordings, compute metrics, and annotate.</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Controls */}
        <div className="w-full lg:w-1/4 space-y-6">
          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-800 mb-4">Record Selection</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Participant</label>
                <select
                  value={selectedPid}
                  onChange={e => {
                    setSelectedPid(e.target.value)
                    setSelectedRecord(null)
                  }}
                  className="w-full border border-slate-300 rounded p-2 text-sm bg-white"
                >
                  {Array.from(new Set(indexData.map(d => d.studyId))).map(pid => (
                    <option key={pid as string} value={pid as string}>{pid as string}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">ECG Record (stableEcgId)</label>
                <select
                  value={selectedRecord?.stableEcgId || ""}
                  onChange={e => setSelectedRecord(participantRecords.find(r => r.stableEcgId === e.target.value))}
                  className="w-full border border-slate-300 rounded p-2 text-sm bg-white"
                >
                  {participantRecords.map(r => (
                    <option key={r.stableEcgId} value={r.stableEcgId}>
                      {r.startTime.split("T")[0]} - {r.classification}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-800 mb-4">View Controls</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Amplitude Unit</label>
                <select value={unit} onChange={e => setUnit(e.target.value)} className="w-full border border-slate-300 rounded p-2 text-sm bg-white">
                  <option value="mV">mV</option>
                  <option value="µV">µV</option>
                  <option value="raw integer">Raw Integer</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Window Length (s): {windowSec}</label>
                <input type="range" min="5" max="30" value={windowSec} onChange={e => setWindowSec(parseInt(e.target.value))} className="w-full" />
              </div>

              {waveform && (
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Start At (s): {startAt}</label>
                  <input type="range" min="0" max={Math.max(0, waveform.total_sec - windowSec)} step="0.5" value={startAt} onChange={e => setStartAt(parseFloat(e.target.value))} className="w-full" />
                </div>
              )}

              <div className="flex items-center">
                <input type="checkbox" id="filter" checked={applyFilter} onChange={e => setApplyFilter(e.target.checked)} className="rounded text-blue-600 mr-2" />
                <label htmlFor="filter" className="text-sm text-slate-700">Apply Bandpass Filter (5-15 Hz)</label>
              </div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-semibold text-slate-800 mb-4">Annotation</h3>
            <div className="space-y-4">
              <div className="flex items-center mb-4 border-b border-slate-100 pb-4">
                <input type="checkbox" id="artifact" checked={artifact} onChange={e => saveArtifact(e.target.checked)} className="rounded text-orange-500 mr-2" />
                <label htmlFor="artifact" className="text-sm font-medium text-slate-700">Mark as Artifact</label>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Diagnostic Label</label>
                <select value={label} onChange={e => setLabel(e.target.value)} className="w-full border border-slate-300 rounded p-2 text-sm bg-white mb-2">
                  <option value="NSR">Normal Sinus Rhythm (NSR)</option>
                  <option value="AF">Atrial Fibrillation (AF)</option>
                  <option value="Other">Other Arrhythmia</option>
                  <option value="Unsure">Unsure</option>
                </select>
                <textarea
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                  placeholder="Additional comments..."
                  className="w-full border border-slate-300 rounded p-2 text-sm resize-none h-20"
                />
                <button onClick={saveLabel} className="mt-2 w-full bg-blue-600 text-white rounded p-2 text-sm font-medium hover:bg-blue-700">
                  Save Label
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Viewer */}
        <div className="w-full lg:w-3/4 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-2">
            {selectedRecord && (
              <div className="px-4 py-3 border-b border-slate-100 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-600">
                <span><strong className="text-slate-800">Start:</strong> {selectedRecord.startTime.replace("T", " ")}</span>
                <span><strong className="text-slate-800">Device Class:</strong> {selectedRecord.classification}</span>
                <span><strong className="text-slate-800">Fs:</strong> {selectedRecord.samplingFrequency || 250.0} Hz</span>
              </div>
            )}

            {waveform ? (
              <div className="h-[400px] w-full">
                <Plot
                  data={[
                    {
                      x: waveform.time,
                      y: waveform.amplitude,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'ECG',
                      line: {color: '#1f77b4'}
                    },
                    {
                      x: waveform.peaks.map((i:number) => waveform.time[i]),
                      y: waveform.peaks.map((i:number) => waveform.amplitude[i]),
                      type: 'scatter',
                      mode: 'markers',
                      name: 'R-Peaks',
                      marker: {color: 'red', size: 6}
                    }
                  ]}
                  layout={{
                    autosize: true,
                    margin: { l: 50, r: 20, t: 30, b: 40 },
                    xaxis: { title: { text: 'Time (s)' } },
                    yaxis: { title: { text: `Amplitude (${unit})` } },
                    showlegend: true,
                    legend: { orientation: 'h', y: 1.1 }
                  }}
                  useResizeHandler={true}
                  style={{width: '100%', height: '100%'}}
                />
              </div>
            ) : (
              <div className="h-[400px] flex items-center justify-center text-slate-400">
                Select a valid record to view waveform
              </div>
            )}
          </div>

          {/* Metrics Panel */}
          {waveform && waveform.metrics && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-semibold text-slate-800">Computed RR Metrics (Current Window)</h3>
                <button onClick={saveMetrics} className="bg-emerald-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-emerald-700 transition-colors">
                  Save Window Metrics
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Heart Rate</p>
                  <p className="text-2xl font-bold text-slate-800">
                    {waveform.metrics.hr ? waveform.metrics.hr.toFixed(1) : "N/A"} <span className="text-sm font-normal text-slate-500">bpm</span>
                  </p>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">RMSSD</p>
                  <p className="text-2xl font-bold text-slate-800">
                    {waveform.metrics.rmssd ? waveform.metrics.rmssd.toFixed(1) : "N/A"} <span className="text-sm font-normal text-slate-500">ms</span>
                  </p>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">SDNN</p>
                  <p className="text-2xl font-bold text-slate-800">
                    {waveform.metrics.sdnn ? waveform.metrics.sdnn.toFixed(1) : "N/A"} <span className="text-sm font-normal text-slate-500">ms</span>
                  </p>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">pNN50</p>
                  <p className="text-2xl font-bold text-slate-800">
                    {waveform.metrics.pnn50 ? waveform.metrics.pnn50.toFixed(1) : "N/A"} <span className="text-sm font-normal text-slate-500">%</span>
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
