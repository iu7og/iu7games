#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "woodcutter.h"

#define WRONG_ARG_NUM 1
#define ALLOCATE_ERROR 3

#define MAX_LEN 401


void free_matrix(int **matrix, const int rows)
{
    for (int i = 0; i < rows; i++)
        free(matrix[i]);

    free(matrix);
}


int **allocate_matrix(const int size)
{
    int **matrix = calloc(size, sizeof(int *));

    if (!matrix)
        return NULL;

    for (int i = 0; i < size; i++)
    {
        matrix[i] = malloc(size * sizeof(int));

        if (!matrix[i])
        {
            free_matrix(matrix, size);
            return NULL;
        }
    }

    return matrix;
}


void fill_matrix(int **matrix, char *string, int size)
{
    for (int i = 0; i < size; i++)
        for (int j = 0; j < size; j++)
            matrix[i][j] = atoi(string[i * size + j]);
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

    int **tree = allocate_matrix(size);

    if (tree == NULL)
    {
        fprintf(stderr, "Allocate error\n");
        return ALLOCATE_ERROR;
    }

    fill_matrix(tree, string, size);

    woodcutter(tree, size);

    free_matrix(tree, size);

    return 0;
}
