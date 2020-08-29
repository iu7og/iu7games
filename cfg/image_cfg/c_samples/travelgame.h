#ifndef TRAVEL_GAME_H
#define TRAVEL_GAME_H

#include <stdio.h>

typedef struct
{
    char origin[4];
    char destination[4];
    int month;
    int day;
} Flight;

int travel_game(int **result, FILE *flights, Flight route);

#endif
