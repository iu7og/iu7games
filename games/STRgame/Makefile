LIB_NAME := split_lib.so

lib.so: *.o
	gcc -shared -o $(LIB_NAME) $^

%.o: %.c
	gcc -c -Wall -Werror -fpic $^

clean: 
	rm *.o *.exe *.so
