import { Send, TriangleAlert, ClipboardList, ArrowUpRight, ArrowDownRight } from "lucide-react"
import { cn } from "@/lib/utils"

type Kpi = {
  label: string
  value: string
  sub: string
  icon: typeof Send
  variant: "default" | "warning"
  trend?: { dir: "up" | "down"; text: string }
}

export function KpiCards({ subscriberCount }: { subscriberCount: number }) {
  const kpis: Kpi[] = [
    {
      label: "Ciudadanos Activos en Telegram",
      value: subscriberCount.toString(),
      sub: "Suscriptos al bot @SAPH_bot",
      icon: Send,
      variant: "default",
      trend: { dir: "up", text: "Registrados hasta hoy" },
    },
    {
      label: "Alertas SMN Activas",
      value: "1 Alerta Naranja",
      sub: "Servicio Meteorológico Nacional",
      icon: TriangleAlert,
      variant: "warning",
      trend: { dir: "up", text: "Vigente hasta 22:00 hs" },
    },
    {
      label: "Reportes de Obstrucción Pendientes",
      value: "12",
      sub: "Sumideros y desagües reportados",
      icon: ClipboardList,
      variant: "default",
      trend: { dir: "down", text: "-3 vs. ayer" },
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {kpis.map((kpi) => {
        const isWarning = kpi.variant === "warning"
        return (
          <div
            key={kpi.label}
            className={cn(
              "relative overflow-hidden rounded-xl border p-5 shadow-sm",
              isWarning ? "border-warning/40 bg-warning text-warning-foreground" : "border-border bg-card text-card-foreground",
            )}
          >
            <div className="flex items-start justify-between gap-4">
              <p className={cn("text-sm font-medium leading-snug", isWarning ? "text-warning-foreground/90" : "text-muted-foreground")}>
                {kpi.label}
              </p>
              <div
                className={cn(
                  "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                  isWarning ? "bg-white/20 text-warning-foreground" : "bg-primary/10 text-primary",
                )}
              >
                <kpi.icon className="h-5 w-5" aria-hidden="true" />
              </div>
            </div>

            <p className="mt-3 text-3xl font-semibold tracking-tight text-balance">{kpi.value}</p>
            <p className={cn("mt-1 text-xs", isWarning ? "text-warning-foreground/80" : "text-muted-foreground")}>
              {kpi.sub}
            </p>

            {kpi.trend && (
              <div
                className={cn(
                  "mt-4 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
                  isWarning
                    ? "bg-white/20 text-warning-foreground"
                    : kpi.trend.dir === "up"
                      ? "bg-success/10 text-success"
                      : "bg-muted text-muted-foreground",
                )}
              >
                {kpi.trend.dir === "up" ? (
                  <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" />
                ) : (
                  <ArrowDownRight className="h-3.5 w-3.5" aria-hidden="true" />
                )}
                {kpi.trend.text}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
