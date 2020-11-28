#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "reagent.h"

#define WRONG_ARG_NUM 1
#define FILE_ERROR 2
#define ALLOCATE_ERROR 3

#define MAX_LEN 401


void free_matrix(char **matrix, const int rows)
{
    for (int i = 0; i < rows; i++)
        free(matrix[i]);

    free(matrix);
}


char **allocate_matrix(const int size)
{
    char **matrix = calloc(size, sizeof(char *));

    if (!matrix)
        return NULL;
    
    for (int i = 0; i < size; i++)
    {
        matrix[i] = malloc(size * sizeof(char));

        if (!matrix[i])
        {
            free_matrix(matrix, size);
            return NULL;
        }
    }

    return matrix;
}


void fill_matrix(char **matrix, char *string, int size)
{
    for (int i = 0; i < size; i++)
        for (int j = 0; j < size; j++)
            matrix[i][j] = string[i * size + j];
}


int main(int argc, char **argv)
{
    if (argc != 3)
    {
        fprintf(stderr, "Wrong arg num\n");
        return WRONG_ARG_NUM;
    }

    const int size = atoi(argv[2]);

    char string[MAX_LEN];
    strcpy(string, argv[1]);

    char **bf = allocate_matrix(size);

    if (bf == NULL)
    {
        fprintf(stderr, "Allocate error\n");
        return ALLOCATE_ERROR;
    }

    fill_matrix(bf, string, size);

    reagent_game(bf, size);

    free_matrix(bf, size);

    return 0;
}

