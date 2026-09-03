import { Truck, MapPin } from "lucide-react"
import { cn } from "@/lib/utils"

type Report = {
  id: string
  barrio: string
  problema: string
  urgencia: "Alta" | "Media" | "Baja"
}


const urgenciaStyles: Record<Report["urgencia"], string> = {
  Alta: "bg-danger/10 text-danger",
  Media: "bg-warning/15 text-warning",
  Baja: "bg-muted text-muted-foreground",
}

export function ReportsTable({ reports }: { reports: Report[] }) {
  return (
    <section className="flex flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
      <header className="flex items-center justify-between border-b border-border px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-card-foreground">Últimos Reportes de Vecinos</h2>
          <p className="text-xs text-muted-foreground">Ingresados vía bot de Telegram</p>
        </div>
        <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
          En vivo
        </span>
      </header>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
              <th scope="col" className="px-5 py-3 font-medium">ID Reporte</th>
              <th scope="col" className="px-5 py-3 font-medium">Barrio</th>
              <th scope="col" className="px-5 py-3 font-medium">Problema</th>
              <th scope="col" className="px-5 py-3 text-right font-medium">Acción</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} className="border-b border-border/60 last:border-0 transition-colors hover:bg-muted/50">
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-card-foreground">{r.id}</span>
                    <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-semibold", urgenciaStyles[r.urgencia])}>
                      {r.urgencia}
                    </span>
                  </div>
                </td>
                <td className="px-5 py-3 text-card-foreground">{r.barrio}</td>
                <td className="px-5 py-3 text-card-foreground">
                  {r.problema}
                </td>
                <td className="px-5 py-3 text-right">
                  <button
                    type="button"
                    className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground transition-opacity hover:opacity-90"
                  >
                    <Truck className="h-3.5 w-3.5" aria-hidden="true" />
                    Desplegar Cuadrilla
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
