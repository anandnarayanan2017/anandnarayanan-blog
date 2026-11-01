import express from "express";
import type { Pool } from "pg";
import type { Router } from "express";
import { errorHandler } from "./http.js";
import { bookingsRouter } from "./routes/bookings.js";
import { roomsRouter } from "./routes/rooms.js";

/** The booking router is injectable so scripts/race.ts can mount the check-then-insert version. */
export function createApp(pool: Pool, bookings: (pool: Pool) => Router = bookingsRouter) {
  const app = express();
  app.use(express.json());
  app.use(roomsRouter(pool));
  app.use(bookings(pool));
  app.use(errorHandler);
  return app;
}
