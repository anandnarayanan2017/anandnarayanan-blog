import type { APIRoute } from "astro";
import { downloadPaths, html } from "../../lib/downloads";

export const getStaticPaths = downloadPaths;

export const GET: APIRoute = ({ props, site }) =>
  new Response(html(props.post, site!), {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
