#!/usr/bin/env bash
set -euo pipefail

# Installs and starts a *user* systemd service that runs auto_pdfocr persistently.

SYSTEMD_USER_DIR="/home/gui/.config/systemd/user"
UNIT="auto-pdfocr.service"

WORKDIR="/home/gui/devel/auto_pdfocr"
UV="/home/gui/.local/bin/uv"

INPUT_DIR="/home/gui/mnt/pdf_input"
OUTPUT_DIR="/home/gui/mnt/pdf_output"

INPUT_MOUNT_UNIT="rclone-pdf-input.service"
OUTPUT_MOUNT_UNIT="rclone-pdf-output.service"

mkdir -p "${SYSTEMD_USER_DIR}"

cat > "${SYSTEMD_USER_DIR}/${UNIT}" <<EOF
[Unit]
Description=auto_pdfocr worker (daemon mode)
Requires=${INPUT_MOUNT_UNIT} ${OUTPUT_MOUNT_UNIT}
After=${INPUT_MOUNT_UNIT} ${OUTPUT_MOUNT_UNIT}

[Service]
Type=simple
WorkingDirectory=${WORKDIR}
ExecStart=${UV} run python main.py --input-dir ${INPUT_DIR} --output-dir ${OUTPUT_DIR} --daemon --interval 60
Restart=on-failure
RestartSec=5

# Graceful stop: our Python loop handles KeyboardInterrupt; send SIGINT.
KillSignal=SIGINT
TimeoutStopSec=30

# Journald logging (default, explicit)
StandardOutput=journal
StandardError=journal

# Hardening (kept reasonable; must be able to access the FUSE mount + write local DB)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictRealtime=true
RestrictSUIDSGID=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
SystemCallArchitectures=native

ReadWritePaths=${WORKDIR} ${INPUT_DIR} ${OUTPUT_DIR}

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "${UNIT}"

# Start this user service at boot even when logged out.
loginctl enable-linger gui

echo "Installed and started: ${UNIT}"

