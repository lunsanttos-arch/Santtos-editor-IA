import {existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const local = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = existsSync(local) ? local : (process.platform === 'win32' ? 'python' : 'python3');
const args = process.argv.slice(2);
const result = spawnSync(python, args[0] === '--test'
  ? ['-m', 'unittest', 'discover', '-s', 'tests', '-v']
  : ['scripts/check_edit.py', ...args], {cwd: root, stdio: 'inherit'});
if (result.error) console.error('Python indisponível. Instale requirements.txt no ambiente Python.', result.error.message);
process.exit(result.status ?? 1);
