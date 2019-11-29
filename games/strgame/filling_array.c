#include <omp.h>

int filling_pointers_array(char **pointers, char *string, int max_len, int words_count)
{
    #pragma omp parallel for
    for (int i = 0; i < words_count; i++)
    {
        pointers[i] = string + i * max_len;
    }
}
