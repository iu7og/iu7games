#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "travelgame.h"

int main(int argc, char **argv)
{
    int *res = NULL;

    FILE *fin = fopen(argv[1], "r");
    Flight flight ={ argv[2], argv[3], atoi(argv[4]), atoi(argv[5]) };

    travel_game(&res, fin, flight);

    fclose(fin);
    free(res);

    return 0;
}
