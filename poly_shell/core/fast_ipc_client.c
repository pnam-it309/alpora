/*
 * Fast IPC Client for ALPORA Poly Shell
 * Connects to the PolyShellDaemon Unix Domain Socket and exchanges JSON in <1ms.
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/un.h>
#include <unistd.h>

#define BUFFER_SIZE 65536
#define DEFAULT_TIMEOUT_SEC 2

static void print_usage(const char *prog_name) {
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "  %s <action> [json_params]   e.g. %s audio.set_volume '{\"percent\": 80}'\n", prog_name, prog_name);
    fprintf(stderr, "  %s <raw_json>               e.g. %s '{\"action\":\"audio.toggle_mute\"}'\n", prog_name, prog_name);
}

static int get_socket_path(char *out_path, size_t max_len) {
    const char *env_sock = getenv("POLY_SHELL_SOCK");
    if (env_sock && env_sock[0] != '\0') {
        if (strchr(env_sock, ':') == NULL) {
            snprintf(out_path, max_len, "%s", env_sock);
            return 0;
        }
    }

    const char *xdg_runtime = getenv("XDG_RUNTIME_DIR");
    if (xdg_runtime && xdg_runtime[0] != '\0') {
        snprintf(out_path, max_len, "%s/poly-shell/ipc.sock", xdg_runtime);
        if (access(out_path, F_OK) == 0) {
            return 0;
        }
    }

    uid_t uid = getuid();
    snprintf(out_path, max_len, "/run/user/%u/poly-shell/ipc.sock", (unsigned int)uid);
    if (access(out_path, F_OK) == 0) {
        return 0;
    }

    /* Fallback candidate locations */
    if (xdg_runtime && xdg_runtime[0] != '\0') {
        snprintf(out_path, max_len, "%s/poly-shell/ipc.sock", xdg_runtime);
        return 0;
    }

    snprintf(out_path, max_len, "/tmp/poly-shell-ipc.sock");
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 2;
    }

    char sock_path[sizeof(((struct sockaddr_un *)0)->sun_path)];
    get_socket_path(sock_path, sizeof(sock_path));

    /* Build payload */
    char payload_buf[BUFFER_SIZE];
    if (argc == 2) {
        if (argv[1][0] == '{') {
            /* Raw JSON */
            snprintf(payload_buf, sizeof(payload_buf), "%s\n", argv[1]);
        } else {
            /* Action only */
            snprintf(payload_buf, sizeof(payload_buf),
                     "{\"id\":\"cli\",\"action\":\"%s\",\"params\":{}}\n", argv[1]);
        }
    } else {
        /* Action + params */
        const char *params = argv[2];
        if (params[0] == '\0') {
            params = "{}";
        }
        snprintf(payload_buf, sizeof(payload_buf),
                 "{\"id\":\"cli\",\"action\":\"%s\",\"params\":%s}\n", argv[1], params);
    }

    int sock_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock_fd < 0) {
        perror("socket");
        return 1;
    }

    /* Set socket timeout */
    struct timeval timeout;
    timeout.tv_sec = DEFAULT_TIMEOUT_SEC;
    timeout.tv_usec = 0;
    setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock_fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    snprintf(addr.sun_path, sizeof(addr.sun_path), "%s", sock_path);

    if (connect(sock_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "poly-ipc-fast: cannot connect to %s: %s\n", sock_path, strerror(errno));
        close(sock_fd);
        return 1;
    }

    /* Send payload */
    size_t len = strlen(payload_buf);
    size_t total_sent = 0;
    while (total_sent < len) {
        ssize_t sent = write(sock_fd, payload_buf + total_sent, len - total_sent);
        if (sent <= 0) {
            perror("poly-ipc-fast write error");
            close(sock_fd);
            return 1;
        }
        total_sent += (size_t)sent;
    }

    /* Read response line */
    char resp_buf[BUFFER_SIZE];
    size_t total_read = 0;
    int got_newline = 0;

    while (total_read < sizeof(resp_buf) - 1) {
        ssize_t n = read(sock_fd, resp_buf + total_read, 1);
        if (n <= 0) {
            break;
        }
        if (resp_buf[total_read] == '\n') {
            got_newline = 1;
            total_read++;
            break;
        }
        total_read++;
    }

    close(sock_fd);

    if (total_read == 0) {
        fprintf(stderr, "poly-ipc-fast: empty response from server\n");
        return 1;
    }

    resp_buf[total_read] = '\0';
    fputs(resp_buf, stdout);
    if (!got_newline) {
        fputc('\n', stdout);
    }
    fflush(stdout);

    /* Check success in response (substring check for quick status) */
    if (strstr(resp_buf, "\"success\": true") || strstr(resp_buf, "\"success\":true")) {
        return 0;
    }
    if (strstr(resp_buf, "\"success\": false") || strstr(resp_buf, "\"success\":false")) {
        return 1;
    }

    return 0;
}
