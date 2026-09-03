import { MapPin, Layers } from "lucide-react"
import { cn } from "@/lib/utils"

type Point = {
  barrio: string
  level: "critico" | "alto" | "medio"
  top: string
  left: string
}

const points: Point[] = [
  { barrio: "Barrio Norte", level: "critico", top: "22%", left: "30%" },
  { barrio: "La Ribera", level: "critico", top: "58%", left: "62%" },
  { barrio: "Villa del Parque", level: "alto", top: "40%", left: "48%" },
  { barrio: "San Martín", level: "alto", top: "70%", left: "28%" },
  { barrio: "Centro", level: "medio", top: "34%", left: "72%" },
  { barrio: "Los Aromos", level: "medio", top: "78%", left: "70%" },
]

const levelStyles: Record<Point["level"], string> = {
  critico: "bg-danger",
  alto: "bg-warning",
  medio: "bg-primary",
}

const legend = [
  { label: "Crítico", dot: "bg-danger" },
  { label: "Alto", dot: "bg-warning" },
  { label: "Medio", dot: "bg-primary" },
]

export function RiskMap() {
  return (
    <section className="flex flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
      <header className="flex items-center justify-between border-b border-border px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-card-foreground">Mapa de Riesgo Hídrico</h2>
          <p className="text-xs text-muted-foreground">Puntos críticos de inundación por barrio</p>
        </div>
        <div className="flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground">
          <Layers className="h-3.5 w-3.5" aria-hidden="true" />
          Capa: Pluvial
        </div>
      </header>

      <div className="relative flex-1 p-5">
        <div
          className="relative h-full min-h-72 w-full overflow-hidden rounded-lg border border-border"
          style={{
            backgroundColor: "oklch(0.93 0.02 235)",
            backgroundImage:
              "linear-gradient(to right, oklch(0.88 0.02 235) 1px, transparent 1px), linear-gradient(to bottom, oklch(0.88 0.02 235) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
          role="img"
          aria-label="Mapa esquemático de la ciudad con puntos de riesgo hídrico por barrio"
        >
          {/* Río simulado */}
          <div
            className="absolute -left-6 top-0 h-full w-24 -rotate-12 rounded-full opacity-70"
            style={{ background: "linear-gradient(180deg, oklch(0.7 0.09 235), oklch(0.62 0.11 250))" }}
            aria-hidden="true"
          />
          {/* Avenida simulada */}
          <div className="absolute left-0 top-1/2 h-1.5 w-full -translate-y-1/2 bg-white/60" aria-hidden="true" />

          {points.map((p) => (
            <div key={p.barrio} className="absolute -translate-x-1/2 -translate-y-1/2" style={{ top: p.top, left: p.left }}>
              <div className="group relative flex flex-col items-center">
                {p.level === "critico" && (
                  <span className={cn("absolute h-6 w-6 animate-ping rounded-full opacity-60", levelStyles[p.level])} aria-hidden="true" />
                )}
                <span className={cn("relative flex h-6 w-6 items-center justify-center rounded-full text-white shadow-md ring-2 ring-white", levelStyles[p.level])}>
                  <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                </span>
                <span className="mt-1 whitespace-nowrap rounded-md bg-card/90 px-1.5 py-0.5 text-[10px] font-medium text-card-foreground shadow-sm">
                  {p.barrio}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-4">
          {legend.map((l) => (
            <div key={l.label} className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className={cn("h-2.5 w-2.5 rounded-full", l.dot)} aria-hidden="true" />
              {l.label}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
