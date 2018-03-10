from django import dispatch

audit_ready = dispatch.Signal()

audit_m2m_ready = dispatch.Signal()
