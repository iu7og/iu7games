#include <string.h>
#include <omp.h>

int check_correctness(char **player_matrix, char **correct_matrix, const int size, const int multiplier)
{
    int sum_errors = 0;

    #pragma omp parallel for reduction(+:sum_errors)
    for (int i = 0; i < size * multiplier; i++)
    {
        if (strcmp(player_matrix[i], correct_matrix[i % size]))
        {
            sum_errors = 0;
        }
    }

    return sum_errors;
}
