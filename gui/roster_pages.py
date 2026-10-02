import streamlit as st
from gui.common import choose, action
from gui.course_pages import DAYS


def show_roster_page(manager):
    st.header('Daily Roster')
    day = st.selectbox('Select a day', DAYS)
    rows = manager.daily_roster(day)
    if rows:
        st.dataframe(rows, hide_index=True, width='stretch')
    else:
        st.info('No lessons scheduled for this day.')
    st.subheader('Student Check-in')
    st.caption('Check-in records course attendance at the current time. It is not tied to the weekday filter above.')
    if manager.students and manager.courses:
        with st.form('check_in'):
            sid = choose('Student', manager.students, 'attendance_student')
            cid = choose('Course', manager.courses, 'attendance_course')
            if st.form_submit_button('Check-in Student'):
                action(manager.check_in, sid, cid)
    else:
        st.info('Add students and courses before checking in.')
    with st.expander('Attendance history'):
        if manager.attendance_log:
            rows = [{**r, 'student_id': str(r['student_id']), 'course_id': str(r['course_id'])} for r in manager.attendance_log]
            st.dataframe(rows, hide_index=True, width='stretch')
        else:
            st.info('No attendance records.')
