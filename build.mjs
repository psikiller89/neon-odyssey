import { compilePack } from "@foundryvtt/foundryvtt-cli";
import fs from "node:fs";
for ( const name of fs.readdirSync("packs/_source") ) {
  const dest = `packs/${name}`;
  fs.rmSync(dest, { recursive: true, force: true });
  await compilePack(`packs/_source/${name}`, dest, { yaml: true, recursive: true, log: false });
  console.log("compiled", name);
}
