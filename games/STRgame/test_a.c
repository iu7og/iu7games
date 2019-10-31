#include <stdio.h>
#define N 100

int split_test(const char *string, char **matrix, const char symbol)
{
    printf("%s:\n %s string\n%c - symbol\n%d - symbol code\n%lu - sizeof(matrix)\n", __func__, string, symbol, symbol, sizeof(matrix));

    int i = 0, count = 0, j = 0;
    while (string[i])
    {
        (!(string[i] == symbol)) ? matrix[count][j++] = string[i] : (matrix[count++][j] = '\0', j = 0);
        ++i;
    }

    matrix[count][j] = '\0';

    for (int i = 0; i < count; i++)
    {
        puts(matrix[i]);
    }

    return ++count;
}

