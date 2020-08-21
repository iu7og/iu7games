#ifndef TRAVEL_GAME_H
#define TRAVEL_GAME_H

#include <stdio.h>

typedef struct
{
    char *origin;
    char *destination;
    int month;
    int day;
} Flight;

int travel_game(int **result, FILE *flights, Flight route);

#endif
