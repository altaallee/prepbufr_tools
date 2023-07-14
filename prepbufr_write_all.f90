program prepbufr_write_all
!
! write all observations out from prepbufr.
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
    real(8)            :: hdr(mxmn), obs(mxmn, mxlv), qcf(mxmn, mxlv), &
                          oer(mxmn, mxlv)

    integer            :: ireadmg, ireadsb

    character(8)       :: subset
    integer            :: table = 24, unit_in = 10, idate
    integer            :: text_out = 11

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
    msg_report: do while (ireadmg(unit_in, subset, idate) == 0)
        sb_report: do while (ireadsb(unit_in) == 0)
            call ufbint(unit_in, hdr, mxmn, 1, iret, hdstr)
            call ufbint(unit_in, obs, mxmn, mxlv, iret, obstr)
            call ufbint(unit_in, oer, mxmn, mxlv, iret, oestr)
            call ufbint(unit_in, qcf, mxmn, mxlv, iret, qcstr)
            write (11, '(a7)') 'message'
            write (11, '(4f14.2)') (hdr(i), i=2, 5)
            do k = 1, iret
                write (11, '(6f15.1)') (obs(i, k), i=1, 6)
            end do
        end do sb_report
   end do msg_report
   call closbf(unit_in)

end program
