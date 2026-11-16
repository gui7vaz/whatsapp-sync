// WhatsApp Sync — background service launcher.
// It exists only so macOS shows a named app ("WhatsApp Sync") in the Full Disk
// Access list. It starts whatsapp_export.py and waits.
#include <libgen.h>
#include <limits.h>
#include <mach-o/dyld.h>
#include <signal.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;
static pid_t child = 0;
static void stop(int sig) { if (child > 0) kill(child, sig); }

int main(void) {
    char buf[PATH_MAX], exe[PATH_MAX], script[PATH_MAX];
    uint32_t n = sizeof(buf);
    if (_NSGetExecutablePath(buf, &n) != 0 || !realpath(buf, exe)) return 1;
    // exe = <project>/WhatsApp Sync.app/Contents/MacOS/whatsapp-sync
    char *dir = exe;
    for (int i = 0; i < 4; i++) dir = dirname(dir);
    snprintf(script, sizeof(script), "%s/whatsapp_export.py", dir);
    setenv("WA_SERVICE", "1", 1);
    // -I: ignore PYTHON* variables, the user site folder and the script folder
    char *args[] = {"/usr/bin/python3", "-I", script, "--no-browser", NULL};
    signal(SIGTERM, stop);
    signal(SIGINT, stop);
    if (posix_spawn(&child, args[0], NULL, NULL, args, environ) != 0) return 1;
    int status = 0;
    while (waitpid(child, &status, 0) < 0) {}
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
