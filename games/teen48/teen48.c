#include <stdio.h>

typedef struct
{
  int rows;
  int columns;
  int **matrix;
} matrix_t;


char teen48game(matrix_t *matrix)
{
    setbuf(stdout, NULL);
    printf("%d cols, %d rows\n", matrix->columns, matrix->rows);
    for (int i = 0; i < 4; i++)
    {
        puts("?");
        for (int j = 0; j < 4; j++)
        {
            //matrix->matrix[i][j] = 228;
            printf("%d ", matrix->matrix[i][j]);
        }
        puts("");
    }

    return 'b';
}
