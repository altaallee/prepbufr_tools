program prepbufr_encode_upperair
!
!  write a upper air observation into prepbufr file
!
! command line arguments
! 1: filename of prepbufr file
! 2: cycle time (YYYYMMDDHH)
! 3: longitude
! 4: latitude
! 5: time
! 6: filename of csv file with mass data
! 7: filename of csv file with wind data
! 8: 1 = append mass data, 0 = do not append
! 9: 1 = append wind data, 0 = do not append
!
   implicit none

   integer, parameter :: mxmn = 35, mxlv = 200
   character(80)      :: hdstr = 'SID XOB YOB DHR TYP ELV SAID T29'
   character(80)      :: obstr = 'POB QOB TOB ZOB UOB VOB PWO CAT PRSS'
   character(80)      :: qcstr = 'PQM QQM TQM ZQM WQM NUL PWQ     '
   character(80)      :: oestr = 'POE QOE TOE NUL WOE NUL PWE     '
   real(8)            :: hdr(mxmn), obs(mxmn, mxlv), qcf(mxmn, mxlv), &
                         oer(mxmn, mxlv)

   character(8)       :: subset
   integer            :: unit_out = 10, unit_table = 20, idate, iret, nlvl = 0

   character(8)       :: c_sid
   real(8)            :: rstation_id
   equivalence(rstation_id, c_sid)

   character(200)     :: pb_filename, char_arg, ds_filename_mass, &
                         ds_filename_wind, csv_line
   integer            :: cycle_time, mass_len, wind_len
   real(8)            :: longitude, latitude, time, alt
   logical            :: pb_exist
   integer            :: unit_ds = 30, iostat

! read command line arguments
   call get_command_argument(1, pb_filename)
   call get_command_argument(2, char_arg)
   read (char_arg, *) cycle_time
   call get_command_argument(3, char_arg)
   read (char_arg, *) longitude
   call get_command_argument(4, char_arg)
   read (char_arg, *) latitude
   call get_command_argument(5, char_arg)
   read (char_arg, *) time
   call get_command_argument(6, ds_filename_mass)
   call get_command_argument(7, ds_filename_wind)
   call get_command_argument(8, char_arg)
   read (char_arg, *) mass_len
   call get_command_argument(9, char_arg)
   read (char_arg, *) wind_len

! check to encode or append
   inquire (file=pb_filename, exist=pb_exist)
   if (pb_exist) then
      ! get bufr table from existing bufr file
      open (unit_table, file='prepbufr.table')
      open (unit_out, file=pb_filename, status='old', form='unformatted')
      call openbf(unit_out, 'IN', unit_out)
      call dxdump(unit_out, unit_table)
      call closbf(unit_out)

      !
      ! write observation into prepbufr file
      !
      open (unit_out, file=pb_filename, status='old', form='unformatted')
      call openbf(unit_out, 'APN', unit_table)
   else
      !
      ! write observation into prepbufr file
      !
      open (unit_table, file='prepbufr.table', action='read')
      open (unit_out, file=pb_filename, action='write', form='unformatted')
      call openbf(unit_out, 'OUT', unit_table)
   end if
   call datelen(10)

   idate = cycle_time ! cycle time: YYYYMMDDHH
   subset = 'ADPUPA'  ! upper-air (raob, drops) reports
   call openmb(unit_out, subset, idate)

   ! set headers
   hdr = 10.0e10
   c_sid = '12345'; hdr(1) = rstation_id
   hdr(2) = longitude; hdr(3) = latitude; hdr(4) = time; hdr(6) = 0.0

   hdr(8) = 31
   obs = 10.0e10; qcf = 10.0e10; oer = 10.0e10

   if (mass_len .gt. 0) then
      open (unit_ds, file=ds_filename_mass)
      do while (iostat == 0)
         read (unit_ds, '(a)', iostat=iostat) csv_line
         nlvl = nlvl + 1

         qcf(1, nlvl) = 1.; qcf(2, nlvl) = 1.; qcf(3, nlvl) = 1.
         qcf(4, nlvl) = 1.; qcf(5, nlvl) = 1.
         oer(1, nlvl) = 1.; oer(2, nlvl) = 1.; oer(3, nlvl) = 1.
         oer(5, nlvl) = 1.

         read (csv_line, *) obs(1, nlvl), obs(2, nlvl), obs(3, nlvl), &
            obs(4, nlvl)
         obs(8, nlvl) = 2.0

      end do

      ! encode obs
      hdr(5) = 132 ! report type: MASS Report - Flight-level reconnaissance and profile dropsonde
      !hdr(5) = 120 ! report type: MASS Report - Rawinsonde
      call ufbint(unit_out, hdr, mxmn, 1, iret, hdstr)
      call ufbint(unit_out, obs, mxmn, nlvl - 1, iret, obstr)
      call ufbint(unit_out, oer, mxmn, nlvl - 1, iret, oestr)
      call ufbint(unit_out, qcf, mxmn, nlvl - 1, iret, qcstr)
      call writsb(unit_out)
   end if

   obs = 10.0e10; qcf = 10.0e10; oer = 10.0e10

   if (wind_len .gt. 0) then
      nlvl = 0
      iostat = 0
      open (unit_ds, file=ds_filename_wind)
      do while (iostat == 0)
         read (unit_ds, '(a)', iostat=iostat) csv_line
         nlvl = nlvl + 1

         qcf(1, nlvl) = 1.; qcf(2, nlvl) = 1.; qcf(3, nlvl) = 1.
         qcf(4, nlvl) = 1.; qcf(5, nlvl) = 1.
         oer(1, nlvl) = 1.; oer(2, nlvl) = 1.; oer(3, nlvl) = 1.
         oer(5, nlvl) = 1.

         read (csv_line, *) obs(1, nlvl), alt, obs(5, nlvl), obs(6, nlvl)
         obs(8, nlvl) = 3.0

      end do

      ! encode obs
      hdr(5) = 232 ! report type: WIND Report - Flight-level reconnaissance and profile dropsonde
      !hdr(5) = 220 ! report type: WIND Report - Rawinsonde
      obs(8, 1) = 3
      call ufbint(unit_out, hdr, mxmn, 1, iret, hdstr)
      call ufbint(unit_out, obs, mxmn, nlvl - 1, iret, obstr)
      call ufbint(unit_out, oer, mxmn, nlvl - 1, iret, oestr)
      call ufbint(unit_out, qcf, mxmn, nlvl - 1, iret, qcstr)
      call writsb(unit_out)
   end if

   call closmg(unit_out)
   call closbf(unit_out)

end program
