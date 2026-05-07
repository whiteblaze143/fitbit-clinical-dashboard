import { Link, useLocation } from "react-router-dom"
import { cn } from "../lib/utils"
import { LayoutDashboard, Users, Activity, FileText } from "lucide-react"

export default function Sidebar() {
  const location = useLocation()

  const links = [
    { name: "Overview", to: "/", icon: LayoutDashboard },
    { name: "Waveforms", to: "/waveforms", icon: Activity },
    { name: "Compliance", to: "/compliance", icon: FileText },
    { name: "Participants", to: "/participants", icon: Users },
  ]

  return (
    <div className="w-64 bg-slate-900 text-slate-100 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-blue-600 to-orange-500">
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <span>🏥</span> Clinical Dashboard
        </h1>
        <p className="text-xs text-blue-100 mt-1 opacity-90">AFib Monitoring Pilot</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon
          const isActive = location.pathname === link.to

          return (
            <Link
              key={link.to}
              to={link.to}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <Icon className="w-5 h-5" />
              {link.name}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
        <p>Sunnybrook Health Sciences Centre</p>
        <p className="mt-1">Version 1.0.0</p>
      </div>
    </div>
  )
}
