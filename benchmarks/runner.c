#define _DEFAULT_SOURCE
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* Keep the launcher small so Python memory is not inherited by the solver. */
int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: runner BINARY INPUT TIMEOUT_SECONDS\n");
        return 1;
    }

    int input = open(argv[2], O_RDONLY);
    int output = open("/dev/null", O_WRONLY);
    if (input < 0 || output < 0) {
        perror("open");
        return 1;
    }

    struct timespec start, finish;
    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) {
        perror("clock_gettime");
        return 1;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return 1;
    }
    if (child == 0) {
        if (dup2(input, STDIN_FILENO) < 0 || dup2(output, STDOUT_FILENO) < 0) {
            perror("dup2");
            _exit(1);
        }
        close(input);
        close(output);
        /* The timeout remains active after exec. */
        alarm((unsigned int) strtoul(argv[3], NULL, 10));
        execl(argv[1], argv[1], (char *) NULL);
        perror("execl");
        _exit(1);
    }
    close(input);
    close(output);

    int status;
    struct rusage usage;
    pid_t waited;
    do {
        waited = wait4(child, &status, 0, &usage);
    } while (waited < 0 && errno == EINTR);
    if (waited < 0) {
        perror("wait4");
        return 1;
    }
    if (clock_gettime(CLOCK_MONOTONIC, &finish) != 0) {
        perror("clock_gettime");
        return 1;
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        fprintf(stderr, "Solver failed with wait status %d\n", status);
        return 1;
    }

    double wall = (double) (finish.tv_sec - start.tv_sec)
                  + (double) (finish.tv_nsec - start.tv_nsec) / 1e9;
    double cpu = (double) usage.ru_utime.tv_sec + (double) usage.ru_stime.tv_sec
                 + (double) (usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1e6;
    printf("{\"wall_seconds\":%.9f,\"cpu_seconds\":%.9f,\"peak_rss_kib\":%ld}\n",
           wall, cpu, usage.ru_maxrss);
    return 0;
}
