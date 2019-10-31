#include <stdio.h>

static char *olds;

char *strtok(char *string, const char *delim)
{
    register int i, j;

    if (string)
        olds = string;

    if ((olds == NULL) || (*olds == '\0'))
        return NULL;

    while(olds)
    {
        for (i = 0; delim[i]; ++i)
            if (*olds == delim[i])
            {
                ++olds;
                break;
            }
        if (!delim[i])
            break;
    }

    if (*olds == '\0')
        return NULL;

    i = 0;
    while (olds[i])
    {
        for (j = 0; delim[j]; ++j)
            if (olds[i] == delim[j])
                goto last_oper;
        ++i;
    }

    last_oper:
        if (olds[i] == '\0')
        {
            olds += i;
            return olds - i;
        }
        olds[i] = '\0';
        olds += i + 1;
        return olds - i - 1;
}
