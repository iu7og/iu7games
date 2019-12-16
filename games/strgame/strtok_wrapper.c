#include <stdlib.h>
#include <dlfcn.h>

void strtok_wrapper(char *player_name, char *string, const char *delim, const int iterations)
{
    char *(*strtok)(char *, const char *);
    void *player_lib = dlopen(player_name, RTLD_NOW);
    strtok = dlsym(player_lib, "strtok");

    strtok(string, delim);
    for (int i = 0; i < iterations; i++)
    {
        strtok(NULL, delim);
    }

    dlclose(player_lib);
}
