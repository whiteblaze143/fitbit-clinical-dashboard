import { useEffect, useState } from "react"
import Layout from "../components/Layout"
import axios from "axios"
import { Activity, Users, FileText, CheckCircle2 } from "lucide-react"

export default function Overview() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    axios.get("/api/study-overview").then(res => setData(res.data)).catch(console.error)
  }, [])

  if (!data) return <Layout><div className="animate-pulse flex space-x-4"><div className="flex-1 space-y-6 py-1"><div className="h-2 bg-slate-200 rounded"></div><div className="space-y-3"><div className="grid grid-cols-3 gap-4"><div className="h-2 bg-slate-200 rounded col-span-2"></div><div className="h-2 bg-slate-200 rounded col-span-1"></div></div></div></div></div></Layout>

  return (
    <Layout>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800">Study Overview</h2>
        <p className="text-slate-500 mt-1">Multi-Participant AFib Monitoring System</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Participants"
          value={data.totalParticipants}
          icon={<Users className="w-6 h-6 text-blue-500" />}
          subtitle="Currently enrolled"
        />
        <MetricCard
          title="Ablation Arm (Pilot)"
          value={`${data.ablationArm} / 10`}
          icon={<Activity className="w-6 h-6 text-orange-500" />}
          subtitle="Post-blanking period"
        />
        <MetricCard
          title="Cardioversion Arm"
          value={`${data.cardioversionArm} / 10`}
          icon={<Activity className="w-6 h-6 text-emerald-500" />}
          subtitle="3-6 month follow-up"
        />
        <MetricCard
          title="Active (48h)"
          value={data.active48h}
          icon={<CheckCircle2 className="w-6 h-6 text-purple-500" />}
          subtitle="Recent ECG data"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-500" />
            Overall Adherence Target
          </h3>
          <span className="px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-full">
            Target: 70%
          </span>
        </div>

        <div className="relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                Current Average
              </span>
            </div>
            <div className="text-right">
              <span className="text-xl font-bold text-blue-600">
                {data.overallCompliance}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-blue-100">
            <div style={{ width: `${Math.min(data.overallCompliance, 100)}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-500"></div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

function MetricCard({ title, value, icon, subtitle }: { title: string, value: string | number, icon: React.ReactNode, subtitle: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-start gap-4">
      <div className="p-3 bg-slate-50 rounded-lg">
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
        <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
      </div>
    </div>
  )
}
