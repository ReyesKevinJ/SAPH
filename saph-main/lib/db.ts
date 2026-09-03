import { drizzle } from "drizzle-orm/better-sqlite3"
import { sqliteTable, integer, text } from "drizzle-orm/sqlite-core"
import Database from "better-sqlite3"
import path from "path"

export const telegramReports = sqliteTable("Reportes", {
  id: integer("id").primaryKey(),
  chat_id: integer("chat_id"),
  tipo_problema: text("tipo_problema"),
  barrio: text("barrio"),
})

export const telegramUsers = sqliteTable("Usuarios", {
  chat_id: integer("chat_id").primaryKey(),
  nombre: text("nombre"),
  barrio: text("barrio"),
})

// SQLite file is at the root of the SAPH repo
const sqlite = new Database(path.resolve(process.cwd(), '../alertas.db'))
export const db = drizzle(sqlite)

export type TelegramReport = typeof telegramReports.$inferSelect
