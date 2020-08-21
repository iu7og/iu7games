#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "travelgame.h"

int main(int argc, char **argv)
{
    int *res = NULL;

    FILE *fin = fopen(argv[1], "r");
    Flight flight = {.month = atoi(argv[4]), .day = atoi(argv[5])};
    strcpy(argv[2], flight.origin);
    strcpy(argv[3], flight.destination);

    travel_game(&res, fin, flight);

    fclose(fin);
    free(res);

    return 0;
}
