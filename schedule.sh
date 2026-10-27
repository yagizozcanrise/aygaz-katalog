#!/bin/sh
# Run publish.sh on this Mac every 4 hours (launchd), so the snapshots stay under the
# tool's 6-hour limit without anyone running it by hand.
#
#   ./schedule.sh install     clone to ~/Library/Application Support/aygaz-katalog, start the job
#   ./schedule.sh uninstall   stop the job and remove the clone
#   ./schedule.sh status      last runs from the log
#
# The job runs from its own clone (git pull before each run) because macOS keeps
# background jobs out of ~/Desktop and ~/Documents. It runs only while the Mac is
# awake and logged in; a run missed during sleep starts on wake. Needs git, python3
# and the GitHub CLI logged in as yagizozcanrise, like publish.sh.
set -eu
label="com.yagizozcanrise.aygaz-katalog"
home="$HOME/Library/Application Support/aygaz-katalog"
plist="$HOME/Library/LaunchAgents/$label.plist"
log="$HOME/Library/Logs/aygaz-katalog.log"
repo="https://github.com/yagizozcanrise/aygaz-katalog.git"

case "${1:-}" in
install)
    if [ -d "$home/.git" ]; then git -C "$home" pull -q; else git clone -q "$repo" "$home"; fi
    mkdir -p "$(dirname "$plist")" "$(dirname "$log")"
    cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$label</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>cd "\$0" &amp;&amp; echo "--- \$(date)" &amp;&amp; git pull -q &amp;&amp; ./publish.sh</string>
        <string>$home</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
    <key>StartInterval</key><integer>14400</integer>
    <key>RunAtLoad</key><true/>
    <key>StandardOutPath</key><string>$log</string>
    <key>StandardErrorPath</key><string>$log</string>
</dict>
</plist>
EOF
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$plist"
    echo "installed: runs now and every 4 hours; log: $log"
    ;;
uninstall)
    launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
    rm -f "$plist"
    rm -rf "$home"
    echo "uninstalled"
    ;;
status)
    launchctl print "gui/$(id -u)/$label" 2>/dev/null | grep -E "state|last exit" || echo "not installed"
    grep -E "^---|published|Error|error" "$log" 2>/dev/null | tail -10
    ;;
*)
    echo "usage: $0 install | uninstall | status" >&2
    exit 2
    ;;
esac
