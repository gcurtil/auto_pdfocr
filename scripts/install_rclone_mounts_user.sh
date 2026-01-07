#!/usr/bin/env bash
set -euo pipefail

# Installs and starts *user* systemd services that mount two OneDrive folders via rclone:
# - Input  (read-only):  onedrive_gcurtil:ds4_scandocs      -> /home/gui/mnt/pdf_input
# - Output (read-write): onedrive_gcurtil:ds4_scandocs_ocr  -> /home/gui/mnt/pdf_output

SYSTEMD_USER_DIR="/home/gui/.config/systemd/user"

# rclone mount requires FUSE userspace helpers (fusermount or fusermount3).
if ! command -v fusermount >/dev/null 2>&1 && ! command -v fusermount3 >/dev/null 2>&1; then
  echo "ERROR: FUSE helpers not found (fusermount / fusermount3). rclone cannot mount."
  echo "Install FUSE (example for Debian/Ubuntu):"
  echo "  sudo apt-get update && sudo apt-get install -y fuse3"
  echo "Then ensure your user can use FUSE and re-run this script."
  exit 1
fi

if [ ! -e /dev/fuse ]; then
  echo "ERROR: /dev/fuse not found. The kernel FUSE module is not loaded or FUSE is not available."
  echo "Try (requires admin):"
  echo "  sudo modprobe fuse"
  echo "Then verify:"
  echo "  ls -la /dev/fuse"
  exit 1
fi

INPUT_REMOTE="onedrive_gcurtil:ds4_scandocs"
OUTPUT_REMOTE="onedrive_gcurtil:ds4_scandocs_ocr"

INPUT_MOUNT="/home/gui/mnt/pdf_input"
OUTPUT_MOUNT="/home/gui/mnt/pdf_output"

INPUT_UNIT="rclone-pdf-input.service"
OUTPUT_UNIT="rclone-pdf-output.service"

mkdir -p "${SYSTEMD_USER_DIR}"
mkdir -p "${INPUT_MOUNT}" "${OUTPUT_MOUNT}"

cat > "${SYSTEMD_USER_DIR}/${INPUT_UNIT}" <<'EOF'
[Unit]
Description=Rclone mount OneDrive input (read-only)
Wants=network-online.target
After=network-online.target

[Service]
Type=simple

# Run in the foreground (no --daemon). systemd supervises restarts.
ExecStart=/usr/bin/rclone mount onedrive_gcurtil:ds4_scandocs /home/gui/mnt/pdf_input \
  --read-only \
  --allow-other \
  --dir-cache-time 5m \
  --poll-interval 15s \
  --attr-timeout 1m \
  --vfs-cache-mode minimal \
  --buffer-size 64M \
  --umask 022 \
  --log-level INFO

ExecStop=/bin/sh -lc 'fusermount -u /home/gui/mnt/pdf_input || fusermount3 -u /home/gui/mnt/pdf_input || true'
Restart=on-failure
RestartSec=5
TimeoutStopSec=30

[Install]
WantedBy=default.target
EOF

cat > "${SYSTEMD_USER_DIR}/${OUTPUT_UNIT}" <<'EOF'
[Unit]
Description=Rclone mount OneDrive output (read-write)
Wants=network-online.target
After=network-online.target

[Service]
Type=simple

# Run in the foreground (no --daemon). systemd supervises restarts.
ExecStart=/usr/bin/rclone mount onedrive_gcurtil:ds4_scandocs_ocr /home/gui/mnt/pdf_output \
  --allow-other \
  --dir-cache-time 5m \
  --poll-interval 15s \
  --attr-timeout 1m \
  --vfs-cache-mode writes \
  --vfs-write-back 5s \
  --buffer-size 64M \
  --umask 022 \
  --log-level INFO

ExecStop=/bin/sh -lc 'fusermount -u /home/gui/mnt/pdf_output || fusermount3 -u /home/gui/mnt/pdf_output || true'
Restart=on-failure
RestartSec=5
TimeoutStopSec=30

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "${INPUT_UNIT}" "${OUTPUT_UNIT}"

# Start these user services at boot even when logged out.
# Enabling lingering typically requires admin privileges.
if loginctl enable-linger gui 2>/dev/null; then
  echo "Enabled lingering for user gui."
else
  echo "Could not enable lingering as the current user. Run this once with admin privileges:"
  echo "  sudo loginctl enable-linger gui"
fi

echo "Installed and started: ${INPUT_UNIT}, ${OUTPUT_UNIT}"
echo "Mountpoints: ${INPUT_MOUNT} (RO), ${OUTPUT_MOUNT} (RW)"
