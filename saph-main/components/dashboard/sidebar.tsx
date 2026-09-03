"use client"

import { useState } from "react"
import { LayoutDashboard, Map, Users, Settings, Droplets, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Mapa de Riesgo", icon: Map, active: false },
  { label: "Usuarios", icon: Users, active: false },
  { label: "Configuraciones", icon: Settings, active: false },
]

export function Sidebar() {
  const [active, setActive] = useState("Dashboard")

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sidebar-primary text-sidebar-primary-foreground">
          <Droplets className="h-5 w-5" aria-hidden="true" />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold">SAPH</p>
          <p className="text-xs text-sidebar-foreground/60">Alerta Hídrica</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3 py-4" aria-label="Navegación principal">
        {navItems.map((item) => {
          const isActive = active === item.label
          return (
            <button
              key={item.label}
              type="button"
              onClick={() => setActive(item.label)}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              <item.icon className="h-[18px] w-[18px]" aria-hidden="true" />
              {item.label}
            </button>
          )
        })}
      </nav>

      <div className="border-t border-sidebar-border px-3 py-4">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-sidebar-accent text-xs font-semibold">
            MG
          </div>
          <div className="min-w-0 flex-1 leading-tight">
            <p className="truncate text-sm font-medium">Mesa de Gestión</p>
            <p className="truncate text-xs text-sidebar-foreground/60">Defensa Civil</p>
          </div>
          <button
            type="button"
            aria-label="Cerrar sesión"
            className="text-sidebar-foreground/50 transition-colors hover:text-sidebar-foreground"
          >
            <LogOut className="h-[18px] w-[18px]" aria-hidden="true" />
          </button>
        </div>
      </div>
    </aside>
  )
}
