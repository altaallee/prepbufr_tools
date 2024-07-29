program prepbufr_decode_all
!
! read all observations out from prepbufr.
! read bufr table from prepbufr file
!
! command line arguments
! 1: filename of prepbufr file
! 2: filename of out file
!
   implicit none

   integer, parameter :: mxmn = 35, mxlv = 250
   character(80)      :: hdstr = 'SID XOB YOB DHR TYP ELV SAID T29'
   character(80)      :: obstr = 'POB QOB TOB ZOB UOB VOB PWO CAT PRSS'
   character(80)      :: qcstr = 'PQM QQM TQM ZQM WQM NUL PWQ     '
   character(80)      :: oestr = 'POE QOE TOE NUL WOE NUL PWE     '
   real(8)            :: hdr(mxmn), obs(mxmn, mxlv), qcf(mxmn, mxlv), oer(mxmn, mxlv)

   integer            :: ireadmg, ireadsb

   character(8)       :: subset
   integer            :: table = 24, unit_in = 10, idate, nmsg, ntb
   integer            :: text_out = 11

   character(8)       :: c_sid
   real(8)            :: rstation_id
   equivalence(rstation_id, c_sid)

   integer            :: i, k, iret

   character(200)     :: filename, out_filename

   open (table, file='prepbufr.table')
   call get_command_argument(1, filename)
   call get_command_argument(2, out_filename)
   open (unit_in, file=filename, form='unformatted', status='old')
   open (text_out, file=out_filename, action='write')
   call openbf(unit_in, 'IN', unit_in)
   call dxdump(unit_in, table)
   call datelen(10)
   nmsg = 0
   msg_report: do while (ireadmg(unit_in, subset, idate) == 0)
      nmsg = nmsg + 1
      ntb = 0
      write (11, *)
      write (11, '(3a,i10)') 'subset=', subset, ' cycle time=', idate
      sb_report: do while (ireadsb(unit_in) == 0)
         ntb = ntb + 1
         call ufbint(unit_in, hdr, mxmn, 1, iret, hdstr)
         call ufbint(unit_in, obs, mxmn, mxlv, iret, obstr)
         call ufbint(unit_in, oer, mxmn, mxlv, iret, oestr)
         call ufbint(unit_in, qcf, mxmn, mxlv, iret, qcstr)
         rstation_id = hdr(1)
         write (11, *)
         write (11, '(a3,2I10,a14,8f15.1)') 'obs', ntb, iret, c_sid, (hdr(i), i=2, 8)
         do k = 1, iret
            write (11, '(i3,a10,9f15.1)') k, 'obs =', (obs(i, k), i=1, 9)
            write (11, '(i3,a10,9f15.1)') k, 'oer =', (oer(i, k), i=1, 7)
            write (11, '(i3,a10,9f15.1)') k, 'qcf =', (qcf(i, k), i=1, 7)
         end do
      end do sb_report
   end do msg_report
   call closbf(unit_in)

end program
