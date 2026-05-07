import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import axios from "axios"

export default function Compliance() {
  const [summaryData, setSummaryData] = useState<any[]>([])

  useEffect(() => {
    axios.get("/api/data/summary").then(res => setSummaryData(res.data)).catch(console.error)
  }, [])

  // Aggregate stats per participant
  const participantStats = Array.from(new Set(summaryData.map(d => d.studyId))).map(pid => {
    const pData = summaryData.filter(d => d.studyId === pid)
    const classifications = pData.reduce((acc, curr) => {
      acc[curr.classification] = (acc[curr.classification] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const lastEcg = pData.length > 0 ? new Date(pData[pData.length - 1].startTime).toLocaleString() : "N/A"
    const total = pData.length

    return {
      studyId: pid,
      total,
      lastEcg,
      classifications
    }
  })

  return (
    <Layout>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Compliance & Adherence</h2>
        <p className="text-slate-500 mt-1">Review participant data uploads and classification summaries.</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mb-8">
        <div className="p-4 border-b border-slate-200 bg-slate-50 font-semibold">
          Data Export Summary by Participant
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Study ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Total ECGs</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Last Sync</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Classifications</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {participantStats.map((p, i) => (
                <tr key={i}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{p.studyId}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{p.total}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{p.lastEcg}</td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(p.classifications).map(([cls, count]) => (
                        <span key={cls} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {cls}: {count as number}
                        </span>
                      ))}
                    </div>
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
