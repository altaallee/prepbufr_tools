program prepbufr_decode_locations
   !
   ! read all observations out from prepbufr.
   ! read bufr table from prepbufr file
   !
   implicit none

   integer, parameter :: mxmn = 35
   character(80):: hdstr = 'SID XOB YOB DHR TYP ELV SAID T29'
   real(8) :: hdr(mxmn)

   integer        :: ireadmg, ireadsb

   character(8)   :: subset
   integer        :: table = 24, unit_in = 10, idate

   character(8)   :: c_sid
   real(8)        :: rstation_id
   equivalence(rstation_id, c_sid)

   integer        :: i, iret

   character(200) :: filename

   open (table, file='prepbufr.table')
   call get_command_argument(1, filename)
   open (unit_in, file=filename, form='unformatted', status='old')
   call openbf(unit_in, 'IN', unit_in)
   call dxdump(unit_in, table)
   call datelen(10)
   msg_report: do while (ireadmg(unit_in, subset, idate) == 0)
      sb_report: do while (ireadsb(unit_in) == 0)
         call ufbint(unit_in, hdr, mxmn, 1, iret, hdstr)
         write (*, '(8f15.1)') (hdr(i), i=2, 8)
      end do sb_report
   end do msg_report
   call closbf(unit_in)

end program
