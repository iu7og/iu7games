
LIB_NAME := split_lib.so
STRTOK_LIB := std_strtok.so
STRTOK_TEST_LIB := strtok_lib.so

strtok_test.so: strtok_test.o
	gcc -shared -o $(STRTOK_TEST_LIB)  $^

strtok.so: strtok.o
	gcc -shared -o $(STRTOK_LIB)  $^
	
lib.so: split_test.o
	gcc -shared -o $(LIB_NAME) $^

%.o: %.c
	gcc -c -Wall -Werror -fpic $^

clean: 
	rm *.o *.exe 

