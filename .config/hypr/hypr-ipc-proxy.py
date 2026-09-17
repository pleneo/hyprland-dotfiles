#!/usr/bin/env python3
import asyncio
import os
import glob
import re
import sys
import signal

run_dir = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")

if not sig:
    hypr_dirs = glob.glob(f"{run_dir}/hypr/*")
    if not hypr_dirs:
        sys.exit(1)
    hypr_dir = hypr_dirs[0]
else:
    hypr_dir = f"{run_dir}/hypr/{sig}"

sock_orig = f"{hypr_dir}/.socket.real.sock"
sock_pub = f"{hypr_dir}/.socket.sock"

# Se o proxy já estiver rodando ou o real.sock não existir, renomeia
if not os.path.exists(sock_orig):
    if os.path.exists(sock_pub):
        os.rename(sock_pub, sock_orig)
    else:
        sys.exit(1)

def translate(text: str) -> str:
    # Trata batch commands se houver
    if text.startswith("[[BATCH]]"):
        cmds = text[9:].split(";")
        tr_cmds = [translate(c.strip()) for c in cmds if c.strip()]
        return "[[BATCH]]" + ";".join(tr_cmds)

    m = re.match(r"^(/?(?:j/)?dispatch\s+)(.*)$", text.strip())
    if m:
        prefix, rest = m.group(1), m.group(2).strip()
        
        # 1. Tratar 'workspace X'
        m_ws = re.match(r"^workspace\s+(.+)$", rest)
        if m_ws:
            arg = m_ws.group(1).strip()
            if arg.isdigit():
                return f"{prefix}hl.dsp.focus({{ workspace = {arg} }})\n"
            else:
                return f'{prefix}hl.dsp.focus({{ workspace = "{arg}" }})\n'
        
        # 2. Tratar 'exec X'
        m_exec = re.match(r"^exec\s+(.+)$", rest)
        if m_exec:
            cmd_str = m_exec.group(1).strip().replace('"', '\\"')
            return f'{prefix}hl.dsp.exec_cmd("{cmd_str}")\n'

    return text

async def handle_client(reader, writer):
    try:
        data = await reader.read(4096)
        if not data:
            writer.close()
            await writer.wait_closed()
            return

        text = data.decode("utf-8", errors="ignore")
        translated_text = translate(text)
        payload = translated_text.encode("utf-8")

        # Conectar ao socket real do Hyprland
        real_reader, real_writer = await asyncio.open_unix_connection(sock_orig)
        real_writer.write(payload)
        await real_writer.drain()

        resp = await real_reader.read(65536)
        writer.write(resp)
        await writer.drain()

        real_writer.close()
        await real_writer.wait_closed()
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    # Remove socket público antigo se sobrou
    if os.path.exists(sock_pub):
        try:
            os.remove(sock_pub)
        except Exception:
            pass

    server = await asyncio.start_unix_server(handle_client, path=sock_pub)
    os.chmod(sock_pub, 0o700)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig_name in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig_name, stop_event.set)

    await stop_event.wait()
    server.close()
    await server.wait_closed()

    # Restaurar socket original ao fechar
    if os.path.exists(sock_orig):
        if os.path.exists(sock_pub):
            os.remove(sock_pub)
        os.rename(sock_orig, sock_pub)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
