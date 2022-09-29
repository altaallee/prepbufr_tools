#! /bin/sh -v

# Define the fortran compiler and options

FC   =  ifort
FLAGS=  -O2 
INCLD=  -I./include
LIBS =  -L./lib -lbufr_i4r8

all: prepbufr_decode_all prepbufr_decode_locations prepbufr_encode_upperair_dawn prepbufr_encode_upperair_dropsonde prepbufr_encode_upperair_halo
up: prepbufr_decode_all prepbufr_decode_locations prepbufr_encode_upperair_dawn prepbufr_encode_upperair_dropsonde prepbufr_encode_upperair_halo

prepbufr_decode_all: prepbufr_decode_all.o
	${FC} -o prepbufr_decode_all.exe ${FLAGS} prepbufr_decode_all.o ${LIBS} 
	rm prepbufr_decode_all.o

prepbufr_decode_locations: prepbufr_decode_locations.o
	${FC} -o prepbufr_decode_locations.exe ${FLAGS} prepbufr_decode_locations.o ${LIBS} 
	rm prepbufr_decode_locations.o

prepbufr_encode_upperair_dawn: prepbufr_encode_upperair_dawn.o
	${FC} -o prepbufr_encode_upperair_dawn.exe ${FLAGS} prepbufr_encode_upperair_dawn.o ${LIBS} 
	rm prepbufr_encode_upperair_dawn.o

prepbufr_encode_upperair_dropsonde: prepbufr_encode_upperair_dropsonde.o
	${FC} -o prepbufr_encode_upperair_dropsonde.exe ${FLAGS} prepbufr_encode_upperair_dropsonde.o ${LIBS} 
	rm prepbufr_encode_upperair_dropsonde.o

prepbufr_encode_upperair_halo: prepbufr_encode_upperair_halo.o
	${FC} -o prepbufr_encode_upperair_halo.exe ${FLAGS} prepbufr_encode_upperair_halo.o ${LIBS} 
	rm prepbufr_encode_upperair_halo.o

.SUFFIXES : .f90  .o

.f90.o :
	${FC} ${FLAGS} ${INCLD} -c $<

clean:
	/bin/rm -f *.o *.exe
