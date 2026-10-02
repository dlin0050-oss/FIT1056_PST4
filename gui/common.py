import streamlit as st


def choose(label, records, key):
    return st.selectbox(label, [r.id for r in records], format_func=lambda i: next(f'{r.name} (ID {r.id})' for r in records if r.id == i), key=key)


def action(function, *args):
    try:
        function(*args)
        st.session_state['notice'] = 'Saved successfully.'
        st.rerun()
    except (ValueError, OSError) as error:
        st.error(str(error))
