import {build} from "esbuild";
import {mkdir, copyFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";

const output = new URL("../backend/web/learning/", import.meta.url);
await mkdir(new URL("assets/", output), {recursive:true});
await build({entryPoints:["src/main.tsx"],bundle:true,minify:true,format:"esm",target:"es2022",
  outfile:fileURLToPath(new URL("assets/app.js",output)),define:{"process.env.NODE_ENV":"\"production\""}});
await copyFile("index.html",new URL("index.html",output));
