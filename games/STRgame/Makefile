lib.so: *.o
	gcc -shared -o test_strgame.so $^

%.o: %.c
	gcc -c -Wall -Werror -fpic $^

clean: 
	rm *.o *.exe *.so in_*
