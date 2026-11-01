/**
 * "Books the boardroom ten times": fires 20 simultaneous booking requests for the same room and slot at the
 * check-then-insert implementation, on a schema without the exclusion constraint, and reports what happened.
 * The result varies from run to run; that is the point. `npm run verify` runs the fixed implementation.
 */
import pg from "pg";
import request from "supertest";
import { createApp } from "../src/app.js";
import { migrate } from "../src/db/migrate.js";
import { bookingsRouter as checkThenInsert } from "../src/routes/bookings-check-then-insert.js";

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL ?? "postgres://postgres:postgres@localhost:5432/rooms",
  max: 20,
});
const fresh = () => pool.query("DROP SCHEMA public CASCADE; CREATE SCHEMA public;");

try {
  await fresh();
  await migrate(pool, (f) => f !== "003_no_overlap.sql");
  const user = async (role: string) =>
    (await pool.query("INSERT INTO users(email, name, role) VALUES (gen_random_uuid()::text, 'u', $1) RETURNING id", [role]))
      .rows[0].id as number;
  const admin = await user("admin");
  const api = () => request(createApp(pool, checkThenInsert));
  const room = (await api().post("/rooms").set("x-user-id", String(admin)).send({ name: "Boardroom", capacity: 12 })).body.id;
  const users = await Promise.all(Array.from({ length: 20 }, () => user("user")));
  const slot = { roomId: room, startAt: "2031-02-01T09:00:00.000Z", endAt: "2031-02-01T10:00:00.000Z" };
  const codes = (await Promise.all(users.map((u) => api().post("/bookings").set("x-user-id", String(u)).send(slot)))).map(
    (r) => r.status,
  );
  const { rows } = await pool.query("SELECT count(*)::int AS n FROM bookings WHERE room_id = $1 AND status = 'confirmed'", [room]);
  const created = codes.filter((c) => c === 201).length;
  console.log(`check-then-insert: ${created} of 20 requests got 201, ${codes.filter((c) => c === 409).length} got 409.`);
  console.log(`The boardroom is booked ${rows[0].n} time(s) for the same hour. The specification allows exactly 1.`);
} finally {
  await fresh(); // leave an empty schema so `npm run verify` starts clean
  await pool.end();
}
