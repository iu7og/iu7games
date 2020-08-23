#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "travelgame.h"

#define WRONG_ARG_NUM 1
#define FILE_ERROR 2

int main(int argc, char **argv)
{
    if (argc != 6)
    {
        fprintf(stderr, "Wrong arg num\n");
        return WRONG_ARG_NUM;
    }

    FILE *fin = fopen(argv[1], "r");
    if (fin == NULL)
    {
        fprintf(stderr, "An error was detected when opening the file\n");
        return FILE_ERROR;
    }

    int *res = NULL;

    Flight flight = {.month = atoi(argv[4]), .day = atoi(argv[5])};
    strcpy(flight.origin, argv[2]);
    strcpy(flight.destination, argv[3]);

    travel_game(&res, fin, flight);

    free(res);
    fclose(fin);

    return 0;
}
