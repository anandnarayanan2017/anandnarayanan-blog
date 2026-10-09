import type { APIRoute } from "astro";
import { downloadPaths, markdown } from "../../lib/downloads";

export const getStaticPaths = downloadPaths;

export const GET: APIRoute = ({ props, site }) =>
  new Response(markdown(props.post, site!), {
    headers: { "Content-Type": "text/markdown; charset=utf-8" },
  });
