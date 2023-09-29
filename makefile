#! /bin/sh -v

# Define the fortran compiler and options

FC   =  ifort
FLAGS=  -O2 
INCLD=  -I./include
LIBS =  -L./lib -lbufr_i4r8

all: prepbufr_decode_all prepbufr_decode_locations prepbufr_encode_upperair_dawn prepbufr_encode_upperair_dropsonde prepbufr_encode_upperair_radiosonde prepbufr_encode_upperair_halo prepbufr_encode_upperair_hamsr prepbufr_write_dropsonde prepbufr_write_all
up: prepbufr_decode_all prepbufr_decode_locations prepbufr_encode_upperair_dawn prepbufr_encode_upperair_dropsonde prepbufr_encode_upperair_radiosonde prepbufr_encode_upperair_halo prepbufr_encode_upperair_hamsr prepbufr_write_dropsonde prepbufr_write_all

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

prepbufr_encode_upperair_radiosonde: prepbufr_encode_upperair_radiosonde.o
	${FC} -o prepbufr_encode_upperair_radiosonde.exe ${FLAGS} prepbufr_encode_upperair_radiosonde.o ${LIBS} 
	rm prepbufr_encode_upperair_radiosonde.o

prepbufr_encode_upperair_halo: prepbufr_encode_upperair_halo.o
	${FC} -o prepbufr_encode_upperair_halo.exe ${FLAGS} prepbufr_encode_upperair_halo.o ${LIBS} 
	rm prepbufr_encode_upperair_halo.o

prepbufr_encode_upperair_hamsr: prepbufr_encode_upperair_hamsr.o
	${FC} -o prepbufr_encode_upperair_hamsr.exe ${FLAGS} prepbufr_encode_upperair_hamsr.o ${LIBS} 
	rm prepbufr_encode_upperair_hamsr.o

prepbufr_write_dropsonde: prepbufr_write_dropsonde.o
	${FC} -o prepbufr_write_dropsonde.exe ${FLAGS} prepbufr_write_dropsonde.o ${LIBS} 
	rm prepbufr_write_dropsonde.o

prepbufr_write_all: prepbufr_write_all.o
	${FC} -o prepbufr_write_all.exe ${FLAGS} prepbufr_write_all.o ${LIBS} 
	rm prepbufr_write_all.o

.SUFFIXES : .f90  .o

.f90.o :
	${FC} ${FLAGS} ${INCLD} -c $<

clean:
	/bin/rm -f *.o *.exe
