import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import axios from "axios"
import { Plus, Save } from "lucide-react"

export default function Participants() {
  const [participants, setParticipants] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchParticipants()
  }, [])

  const fetchParticipants = async () => {
    try {
      const res = await axios.get("/api/participants")
      setParticipants(res.data)
      setLoading(false)
    } catch (e) {
      console.error(e)
    }
  }

  const addParticipant = () => {
    setParticipants([...participants, {
      studyId: "", firstName: "", lastName: "", phone: "", email: "",
      deviceId: "", status: "invited", startDate: "", endDate: "",
      expectedPerDay: "2", notes: ""
    }])
  }

  const saveParticipants = async () => {
    try {
      await axios.post("/api/participants", { participants })
      alert("Saved successfully!")
    } catch (e) {
      alert("Failed to save")
    }
  }

  const updateParticipant = (index: number, field: string, value: string) => {
    const newP = [...participants]
    newP[index][field] = value
    setParticipants(newP)
  }

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Participant Registry</h2>
          <p className="text-slate-500 mt-1">Manage enrolled participants and their details.</p>
        </div>
        <div className="flex gap-3">
          <button onClick={addParticipant} className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 hover:bg-slate-50">
            <Plus className="w-4 h-4" /> Add Participant
          </button>
          <button onClick={saveParticipants} className="flex items-center gap-2 px-4 py-2 bg-blue-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700">
            <Save className="w-4 h-4" /> Save Changes
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                {["Study ID", "First Name", "Last Name", "Email", "Status", "Device ID", "Start Date", "Expected/Day"].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {loading ? (
                <tr><td colSpan={8} className="px-6 py-4 text-center text-sm text-slate-500">Loading...</td></tr>
              ) : participants.length === 0 ? (
                <tr><td colSpan={8} className="px-6 py-4 text-center text-sm text-slate-500">No participants found. Add one above.</td></tr>
              ) : participants.map((p, i) => (
                <tr key={i}>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="text" value={p.studyId || ""} onChange={e => updateParticipant(i, "studyId", e.target.value)} className="w-24 px-2 py-1 border border-slate-300 rounded text-sm focus:ring-blue-500 focus:border-blue-500" placeholder="ABL01" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="text" value={p.firstName || ""} onChange={e => updateParticipant(i, "firstName", e.target.value)} className="w-24 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="text" value={p.lastName || ""} onChange={e => updateParticipant(i, "lastName", e.target.value)} className="w-24 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="text" value={p.email || ""} onChange={e => updateParticipant(i, "email", e.target.value)} className="w-40 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <select value={p.status || "invited"} onChange={e => updateParticipant(i, "status", e.target.value)} className="w-28 px-2 py-1 border border-slate-300 rounded text-sm bg-white">
                      <option value="invited">Invited</option>
                      <option value="enrolled">Enrolled</option>
                      <option value="paused">Paused</option>
                      <option value="withdrawn">Withdrawn</option>
                    </select>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="text" value={p.deviceId || ""} onChange={e => updateParticipant(i, "deviceId", e.target.value)} className="w-24 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="date" value={p.startDate || ""} onChange={e => updateParticipant(i, "startDate", e.target.value)} className="w-36 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <input type="number" value={p.expectedPerDay || ""} onChange={e => updateParticipant(i, "expectedPerDay", e.target.value)} className="w-16 px-2 py-1 border border-slate-300 rounded text-sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  )
}
